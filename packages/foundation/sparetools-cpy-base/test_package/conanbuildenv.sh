script_folder="/home/sparrow/projects/dev-tools/sparetools/packages/foundation/sparetools-cpy-base/test_package"
echo "echo Restoring environment" > "$script_folder/deactivate_conanbuildenv.sh"
for v in PYTHONHOME PATH PYTHON_ROOT LD_LIBRARY_PATH
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "$script_folder/deactivate_conanbuildenv.sh"
    else
        echo unset $v >> "$script_folder/deactivate_conanbuildenv.sh"
    fi
done


export PYTHONHOME="/home/sparrow/.conan2/p/b/spare396afff651504/p"
export PATH="/home/sparrow/.conan2/p/b/spare396afff651504/p/bin:/home/sparrow/.conan2/p/b/spare396afff651504/p/bin:$PATH"
export PYTHON_ROOT="/home/sparrow/.conan2/p/b/spare396afff651504/p"
export LD_LIBRARY_PATH="/home/sparrow/.conan2/p/b/spare396afff651504/p/lib:$LD_LIBRARY_PATH"