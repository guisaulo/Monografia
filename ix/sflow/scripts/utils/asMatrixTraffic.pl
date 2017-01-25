#!/usr/bin/perl -w
use strict;
use POSIX;

open(PS, "/usr/local/bin/sflowtool|") || die "Failed: $!\n";
while( <PS> ) {  
  my ($attr,$value) = split;
 
  # process attribute  
}

close(PS);
