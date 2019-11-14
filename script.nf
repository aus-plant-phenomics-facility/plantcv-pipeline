process query_snapshots {
	input:
		file query_file from file("$params.query_file")

    output:
        file "job*.json" into jobs_ch

    script:
    if (params.image_limit)
	    """
	    01-query-snapshots.py $params.database_server $params.database $params.database_user $params.database_password "$params.measurement_label" "$query_file" --limit $params.image_limit

	    """
	else
	    """
	    01-query-snapshots.py $params.database_server $params.database $params.database_user $params.database_password "$params.measurement_label" "$query_file"

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
	  if( params.image_access_method == 'sftp' )
		"""
		02a-fetch-image.py $job_file $params.image_server $params.image_user $image_pkey $params.image_base_dir$params.database
		"""
	else ( params.image_access_method == 'local' )
		"""
		02ax-symlink-image.py $job_file $params.image_base_dir$params.database
		"""
	


}

process analyse_image {

    input:
        set val(id), file(job_file), file(image_file) from input_image_ch

	output:
		file "result_${job_file.baseName}.json" into results_ch
		file "*.png" optional true
	
	script:
	"""
		02b-analyse-image.py -i $image_file -m $job_file -o "." -r "result_${job_file.baseName}.json" -w -D '$params.debug'
	"""

	
}

process aggregate_results {

	publishDir 'results'
	
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
