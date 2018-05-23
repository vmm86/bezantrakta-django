#!/bin/bash

echo "Создание документации для администраторов..."
echo ""
cd docs/adm
make html

echo ""

echo  "Создание документации для разработчиков..."
echo ""
cd ../../docs/dev
make html
