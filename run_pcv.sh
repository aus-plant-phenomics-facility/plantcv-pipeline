for d in 0438_PH_UA_Garnett_Wheat/*/; do

ID=$(echo "$d" | grep -oE "([^_]*_2018-07-02)")
echo $ID

mkdir -p "results"

python plantcv-vis.py -i "$d/RGB_3D_3D_side_far_0/0_0_0.png" -r "results/$ID.json" -w #-o "output/$ID"

done
