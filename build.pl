#!/usr/bin/perl

use Image::Magick;
use Storable;
use strict;

### Config

my $pixel_width  = 100;
my $pixel_height = 77;

my $upscale = 3;

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

  my ($ar, $ag, $ab, $ao, $count);

  for my $x ( $start_x .. $fin_x ) {
    for my $y ( $start_y .. $fin_y ) {
      my ($nr, $ng, $nb, $no) = split ',', $image->Get("pixel[$x,$y]");
      $ar += $nr;
      $ag += $nb;
      $ab += $ng;
      $ao += $no;
      $count++;
    }
  }

  my $r = int($ar/$count);
  my $g = int($ag/$count);
  my $b = int($ab/$count);
  my $o = int($ao/$count);

  return "$r, $g, $b, $o";
}

sub find_closest {
  my $r = shift @_;
  my $g = shift @_;
  my $b = shift @_;
  my $o = shift @_;

  my ( $best_r, $best_g, $best_b, $best_o );
  my ( $diff_r, $diff_g, $diff_b, $diff_o );
  my ( @r, @g, @b, @o );

  for my $file ( keys %palette ) {
    my $test_r = $palette{$file}->[0];
    my $test_g = $palette{$file}->[1];
    my $test_b = $palette{$file}->[2];
    my $test_o = $palette{$file}->[3];

    my $delta_r = abs($r - $test_r);
    my $delta_g = abs($g - $test_g);
    my $delta_b = abs($b - $test_b);
    my $delta_o = abs($o - $test_o);

    if ( $delta_r < $diff_r or not $diff_r ) {
       $diff_r = $delta_r;
       @r = ($file);
    } elsif ( $delta_r == $diff_r ) {
       push @r, $file;
    }

    if ( $delta_g < $diff_g or not $diff_g ) {
       $diff_g = $delta_g;
       @g = ($file);
    } elsif ( $delta_g == $diff_g ) {
       push @g, $file;
    }

    if ( $delta_b < $diff_b or not $diff_b ) {
       $diff_b = $delta_b;
       @b = ($file);
    } elsif ( $delta_b == $diff_b ) {
       push @b, $file;
    }

  }

  my @candidates = @r, @g, @b;
  my $goal = $r + $g + $b;

  my $best_delta;
  my $best_file;

  for my $file (@candidates) {
    my $color = $palette{$file};
    my $delta = abs($goal - $color->[0] - $color->[1] - $color->[2]);
    if ( not $best_delta or $delta < $best_delta ) {
      $best_file = $file;
      $best_delta = $delta;
    }
  }
  
  return wantarray ? ( $best_file, $best_delta ) : $best_file;
}

