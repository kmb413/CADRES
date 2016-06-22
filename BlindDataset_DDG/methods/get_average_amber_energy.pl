#!/usr/bin/perl

open (G,$ARGV[0]);

while (<G>){

	chomp($_);
	$lines++;
	if ($lines>1){
	@spl = split(/,/,$_);
	$energy[$spl[0]] = $spl[1];
#	print $spl[0]." ".$spl[1]."\n";
	}
}
close G;

open (F,$ARGV[1]);

while (<F>)
{	
	chomp($_);
	@spl = split (/,/,$_);
	@spl2 = split (/\s+/, $spl[1]);
#	print $spl2[2]."\n";

	@spl3 = split (/\+/, $spl2[2]);
		
	for ($i=0;$i<=$#spl3;$i++)
		{
			$energy_total += $energy[$spl3[$i]]; 
		} 
	$average_energy[$count] = $energy_total/($#spl3+1);
#	print $#spl3."\n";
#	print $average_energy[$count]."\n";
	$count++;
	$energy_total = 0; 
}
#print $count."\n";

for ($j=0;$j<=$count;$j++)
{
	$overall_average += $average_energy[$j];
}

print ($overall_average/$count);
print "\n";
close F;	
