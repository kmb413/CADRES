#!/bin/bash

dir=$1

cd $dir

for subdir in $(ls -l | grep '^d' | awk '{print $9}')
do

	cd $subdir

	for scorefile in $(ls *.sc)
	do
		cp $scorefile '../'$subdir'.sc'
	done
	
	cd ../

done
