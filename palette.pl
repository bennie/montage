#!/usr/bin/perl

use Image::Magick;
use Storable;

use strict;
use warnings;

my $out = shift @ARGV;

my %palette;

for my $file (@ARGV) {
  next unless -r $file;

  my $image = Image::Magick->new;
  my $ret = $image->Read($file);
  warn "$ret" if $ret;

  my $max = $image->MaxRGB;

  my $ar = my $ag = my $ab = my $count = 0;

  my $width  = $image->Get('width' );
  my $height = $image->Get('height');

  for my $x ( 0 .. $width ) {
    for my $y ( 0 .. $height ) {
      my ($nr, $ng, $nb, $nu) = split ',', $image->Get("pixel[$x,$y]");
      $ar += $nr;
      $ag += $nb;
      $ab += $ng;
      $count++;
    }
  }

  my $r = int($ar/$count);
  my $g = int($ag/$count);
  my $b = int($ab/$count);

  $palette{$file} = [ $r, $g, $b, $max ];
  print "$r $g $b ($max) : $file\n";
}

store \%palette, $out;
