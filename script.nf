import java.nio.file.Paths


process query_snapshots {
	input:
		file query_file from file(params.query_file)

	output:
		file "job*.json" into jobs_ch

	script:
		"""
		01-query-snapshots.py $params.db_srv $params.db $params.db_usr $params.db_pw "$params.measurement_label" "$query_file" --limit $params.limit

		"""
}

image_pkey_ch = file(params.image_pkey)

process fetch_image {

	maxRetries = 3

	errorStrategy { 
		if(task.exitStatus == 15){
			if(task.attempt == 3){
				'ignore'
			}else{
				'retry'
			}
		}else{
			'terminate'
		}
	}


	input:
		file job_file from jobs_ch.flatten()
		file image_pkey from image_pkey_ch

	output:
		set val(job_file.baseName), file(job_file), file("input_image.png") into input_image_ch

	script:
		image_dir_joined = Paths.get(params.image_base_dir, params.db)
		if ( params.image_access_method == 'local' )
			"""
			02ax-symlink-image.py $job_file $image_dir_joined
			"""
		else //if( params.image_access_method == 'sftp' )
			"""
			02a-fetch-image.py $job_file $params.image_server $params.image_user $image_pkey $image_dir_joined
			"""
}

process analyse_image {

	if (params.debug == 'print' || params.write_image == 'write')
		publishingEnabled = true
	else
		publishingEnabled = false

	publishDir "images", enabled: publishingEnabled

	input:
		set val(id), file(job_file), file(image_file) from input_image_ch

	output:
		file "result_${job_file.baseName}.json" into results_ch
		file "result_${job_file.baseName}*.png" optional true into output_images_ch
	
	script:
		if (params.write_image == 'write')
		"""
			02b-analyse-image.py -i $image_file -m $job_file -o . -r "result_${job_file.baseName}.json" -D '$params.debug' -w
		"""
		else //if ( params.write_image == 'none' )
		"""
			02b-analyse-image.py -i $image_file -m $job_file -o . -r "result_${job_file.baseName}.json" -D '$params.debug'
		"""
	
}

process aggregate_results {

	publishDir 'results', mode: 'copy'
	
	input:
		file results from results_ch.collect()

	output:
		file "merged.json"
		file "merged*.csv"

	script:
		"""
		03-aggregate-results.py
		"""
}
