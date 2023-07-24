#!/bin/bash

x=`echo "$1 * -1 + 90" | bc`
y=`echo "$2 * 1 + 126" | bc`
z=`echo "$3 * 1 + 72" | bc` 

echo $x $y $z

