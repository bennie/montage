#!/usr/bin/env perl

use Image::Magick;
use Math::Complex;
use Storable;

use strict;
use warnings;

### Config

my $pixel_width  = 100;
my $pixel_height = 77;

my $upscale = 10;

#my $pixel_width  = 20;
#my $pixel_height = 15;

### Main

my $palette_db   = shift @ARGV;
my $goal_image   = shift @ARGV;
my $output_image = shift @ARGV;

my %palette = %{ retrieve $palette_db };
my $num_pixels = scalar(keys %palette);

print STDERR "We have $num_pixels potential pixel images\n";

my $goal = Image::Magick->new;
my $ret = $goal->Read($goal_image);
warn "$ret" if $ret;

my $width  = $goal->Get('width' ) * $upscale;
my $height = $goal->Get('height') * $upscale;

print STDERR "Our output should be $width x $height (upscale $upscale)\n";

### Analyse

my %locations;
my $count = 1;

my $start_x = 0;
while ( $start_x < $width ) {
  my $fin_x = $start_x + $pixel_width;
  my $start_y = 0;
  while ( $start_y < $height ) {
    my $fin_y = $start_y + $pixel_height;

    my @color = &color_check($goal,$start_x,$start_y,$fin_x,$fin_y,$upscale);
    my ($file,$delta) = &find_closest(@color);

    print "$count: $start_x x $start_y : $delta : $file\n";

    $locations{$file}{$start_x}{$start_y}++;

    $count++;
    $start_y = $fin_y;
  }
  $start_x = $fin_x;
}

$goal = undef;

### Write Image

print STDERR "\nWriting the output image ($output_image) of $count tiles\n";

my $out = new Image::Magick (
  background => 'white',
  colorspace => 'RGB',
  size       => $width.'x'.$height,
);

$ret = $out->ReadImage('xc:red');
warn $ret if $ret;

for my $file ( sort keys %locations ) {
  print "$file : ";

  my $img = new Image::Magick;
  my $ret = $img->Read($file);
  warn $ret if $ret;

  $ret = $img->Scale(height=>$pixel_height,width=>$pixel_width);
  warn $ret if $ret;

  my $total_count = 0;
  for my $x ( keys %{$locations{$file}} ) {
    for my $y ( keys %{$locations{$file}{$x}} ) {
      $total_count++;
    }
  }

  my $count = 0;
  for my $x ( keys %{$locations{$file}} ) {
    for my $y ( keys %{$locations{$file}{$x}} ) {
      $count++;
      print "\r$file : $count / $total_count";
      $out->Composite(image=>$img,compose=>'Atop',x=>$x,y=>$y);
    }
  }

  print "\n";
}

$ret = $out->Write(filename=>$output_image);
warn $ret if $ret;

### Subroutines

sub color_check {
  my $image   = shift @_;
  my $start_x = shift @_ || 0; 
  my $start_y = shift @_ || 0; 
  my $fin_x   = shift @_ || $image->Get('width' );
  my $fin_y   = shift @_ || $image->Get('height');
  my $upscale = shift @_ || 1;

  $start_x = int($start_x/$upscale);
  $start_y = int($start_y/$upscale);
  $fin_x = $fin_x % $upscale ? int($fin_x/$upscale)+1 : int($fin_x/$upscale);
  $fin_y = $fin_y % $upscale ? int($fin_y/$upscale)+1 : int($fin_y/$upscale);

  my ($ar, $ag, $ab, $count);

  for my $x ( $start_x .. $fin_x ) {
    for my $y ( $start_y .. $fin_y ) {
      my ($nr, $ng, $nb, $no) = split ',', $image->Get("pixel[$x,$y]");
      $ar += $nr;
      $ag += $nb;
      $ab += $ng;
      $count++;
    }
  }

  my $max = $image->MaxRGB;

  my $r = int($ar/$count);
  my $g = int($ag/$count);
  my $b = int($ab/$count);

  return ($r, $g, $b, $max);
}

sub find_closest {
  my ($r,$g,$b) = &resample(@_);

  my @best;
  my $dist = 450; # 8 bit color reduced

  for my $file ( keys %palette ) {
    my ($tr,$tg,$tb) = &resample(@{$palette{$file}});

    my $tdist = int( sqrt(($r-$tr)**2 + ($g-$tg)**2 + ($b-$tb)**2) );

    if ( $tdist < $dist ) {
      @best = ( $file );
      $dist = $tdist;
    } elsif ( $dist == $tdist ) {
      push @best, $file;
    }
  }

  warn "Dist: $dist\n" if $dist <= 0;

  my $rand = $best[int rand($#best + 1)];

  return wantarray ? ( $rand, "$dist ".scalar(@best) ) : $rand;
}

sub resample {
  my $r_in  = $_[0];
  my $g_in  = $_[1];
  my $b_in  = $_[2];
  my $depth = $_[3];

  my $resample_factor = ( $depth + 1 ) / 256;

  my $r = int($r_in/$resample_factor);
  my $g = int($g_in/$resample_factor);
  my $b = int($b_in/$resample_factor);

  $r++ if $r_in % $resample_factor;
  $g++ if $g_in % $resample_factor;
  $b++ if $b_in % $resample_factor;

  return ($r,$g,$b);
}
