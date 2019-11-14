SELECT
   snapshot.id_tag AS "Plant ID",
   metadata_view."Genotype ID",
   metadata_view."Watering Regime",
   metadata_view."Replicate",
   metadata_view."Smarthouse",
   metadata_view."Lane",
   metadata_view."Position",
   to_char(time_stamp,'YYYY-MM-DD_HH24-MI-SS') as "Time",
   DATE_PART('day', snapshot.time_stamp - '2019-01-09') as "Time After Planting",
   snapshot.water_amount AS "Water Amount",
   snapshot.weight_after AS "Weight After",
   snapshot.weight_before AS "Weight Before",
   camera_label,
   path
FROM
   snapshot 
   LEFT JOIN
      metadata_view 
      ON snapshot.id_tag = metadata_view.id_tag 
       JOIN tiled_image 
         ON snapshot.id = tiled_image.snapshot_id 
       JOIN tile 
         ON tiled_image.id = tile.tiled_image_id 
       JOIN image_file_table 
         ON tile.image_oid = image_file_table.id    
WHERE
   snapshot.id_tag ~ '^\d+ ?' 
   AND snapshot.measurement_label = '{measurement_label}'
   AND camera_label like '%RGB%'
ORDER BY
   camera_label,
   time_stamp desc,
   "Plant ID"