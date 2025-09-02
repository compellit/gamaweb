#!/bin/bash

# Initialize flags
run_localization=false
run_collectstatic=false

# Parse command line arguments
while getopts "lc" opt; do
    case ${opt} in
        l )
            run_localization=true
            ;;
        c )
            run_collectstatic=true
            ;;
        \? )
            echo "Usage: $0 [-l] [-c]"
            echo "  -l: Run localization commands (makemessages and compilemessages)"
            echo "  -c: Run collectstatic command"
            exit 1
            ;;
    esac
done

# Check if no arguments were provided
if [ "$run_localization" = false ] && [ "$run_collectstatic" = false ]; then
    echo "Usage: $0 [-l] [-c]"
    echo "  -l: Run localization commands (makemessages and compilemessages)"
    echo "  -c: Run collectstatic command"
    echo "Please specify at least one option."
    exit 1
fi

# Run localization commands if -l flag is set
if [ "$run_localization" = true ]; then
    echo "Running localization commands..."
    python manage.py makemessages -l fr
    python manage.py makemessages -l gl
    python manage.py compilemessages
    echo "Localization commands completed."
fi

# Run collectstatic if -c flag is set
if [ "$run_collectstatic" = true ]; then
    echo "Running collectstatic..."
    python manage.py collectstatic
    echo "Collectstatic completed."
fi

# -n 1 means read will stop after 1 character
read -n 1 -p "Run migrations? [y/n] " answer
echo

case $answer in
    [yY])
        echo "Doing migrations"
        python manage.py makemigrations
	python manage.py migrate
        ;;
    [nN])
        echo "No migrations asked for."
        ;;
    *)
        echo "Invalid option for migrations."
        ;;
esac

echo "Script execution finished."
