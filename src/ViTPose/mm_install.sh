git clone https://github.com/open-mmlab/mmcv.git
git checkout v1.3.9
cd mmcv
MMCV_WITH_OPS=1 pip install -e .
cd ../
rm -rf mmcv


git clone https://github.com/open-mmlab/mmpose.git
mkdir -p /mmpose/data
cd mmpose
pip install --no-cache-dir -e .
cd ../
rm -rf mmpose