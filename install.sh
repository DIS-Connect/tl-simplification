
python setup.py bdist_wheel
pip install dist/tl_simplification-0.1.0-py3-none-any.whl --force

rm -rf .eggs
rm -rf build
rm -rf dist
rm -rf tl_simplification.egg-info