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

  my ($ar, $ag, $ab, $au, $count);

  my $width  = $image->Get('width' );
  my $height = $image->Get('height');

  for my $x ( 0 .. $width ) {
    for my $y ( 0 .. $height ) {
      my ($nr, $ng, $nb, $nu) = split ',', $image->Get("pixel[$x,$y]");
      $ar += $nr;
      $ag += $nb;
      $ab += $ng;
      $au += $nu;
      $count++;
    }
  }

  my $r = int($ar/$count);
  my $g = int($ag/$count);
  my $b = int($ab/$count);
  my $u = int($au/$count);

  $palette{$file} = [ $r, $g, $b, $u ];
  print "$r $g $b $u : $file\n";
}

store \%palette, $out;
