script_folder="/home/sparrow/projects/dev-tools/sparetools/packages/python/sparetools-py/test_package"
echo "echo Restoring environment" > "$script_folder/deactivate_conanbuildenv.sh"
for v in PYTHON_ROOT PATH LD_LIBRARY_PATH PYTHONHOME PYTHONPATH DYLD_LIBRARY_PATH
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


export PYTHON_ROOT="/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p"
export PATH="/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p/bin:/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p/bin:/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p/bin:$PATH"
export LD_LIBRARY_PATH="/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p/lib:/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p/lib:$LD_LIBRARY_PATH"
export PYTHONHOME="/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p"
export PYTHONPATH="$PYTHONPATH:/home/sparrow/.conan2/p/b/spare44845c575afa9/p:/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p/lib/python3.12"
export DYLD_LIBRARY_PATH="/home/sparrow/.conan2/p/b/sparee571a54d28e0e/p/lib:$DYLD_LIBRARY_PATH"