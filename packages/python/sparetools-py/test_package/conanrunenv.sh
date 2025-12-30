script_folder="/home/sparrow/projects/dev-tools/sparetools/packages/python/sparetools-py/test_package"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv.sh"
for v in PYTHONPATH SPARETOOLS_PY_PACKAGE_DIR
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "$script_folder/deactivate_conanrunenv.sh"
    else
        echo unset $v >> "$script_folder/deactivate_conanrunenv.sh"
    fi
done


export PYTHONPATH="$PYTHONPATH:/home/sparrow/.conan2/p/b/spare44fde7fc0285e/p"
export SPARETOOLS_PY_PACKAGE_DIR="/home/sparrow/.conan2/p/b/spare44fde7fc0285e/p"