process query_snapshots {
    output:
        file "job*.json" into jobs_ch

    script:
    """
    01-query-snapshots.py $params.database_server $params.database $params.database_user $params.database_password "$params.measurement_label" --limit $params.image_limit

    """

}

image_pkey_ch = file(params.image_pkey)

process fetch_image {
	input:
	    file job_file from jobs_ch.flatten()
	    file image_pkey from image_pkey_ch

	output:
		file "input_image.png" into input_image_ch

	script:
	"""
	02a-fetch-image.py $job_file $params.image_server $params.image_user $image_pkey $params.image_base_dir$params.database
	"""
}

process analyse_image {

    input:
        file "input_image.png" from input_image_ch
	    file job_file from jobs_ch.flatten()

	output:
		file "result_${job_file.baseName}.json" into results_ch
		file "*.png" optional true
	
	script:
	"""
		02b-analyse-image.py -i input_image.png -m $job_file -o "." -r "result_${job_file.baseName}.json" -w -D 'none'
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
