#!/bin/bash

# Change to the correct directory
#cd /home/martin/desarrollo/tareas/tareas_back/app || exit

# Run make html command
make html

# Find and replace the string in _build folder
find _build -type f -exec sed -i 's/ <span>conestack<\/span>/ <span>Tareas SCJ<\/span>/g' {} +

echo "Build completed and replacements made."

. start.sh