script_folder="/home/sparrow/projects/dev-tools/sparetools/packages/testing/sparetools-cpy-hil/test_package"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv.sh"
for v in PYTHONPATH PYTHONHOME PATH
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


export PYTHONPATH="/home/sparrow/.conan2/p/b/spare190e90bef20ae/p/lib/python3.12/site-packages:$PYTHONPATH:/home/sparrow/.conan2/p/b/spare0bae7766f03fa/p/lib/python3.12"
export PYTHONHOME="/home/sparrow/.conan2/p/b/spare0bae7766f03fa/p"
export PATH="/home/sparrow/.conan2/p/b/spare0bae7766f03fa/p/bin:/home/sparrow/.conan2/p/b/spare0bae7766f03fa/p/bin:$PATH"