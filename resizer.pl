#!/opt/local/bin/perl
#
# Copyright (C) 1999-2002, Phillip Pollard
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by 
#  the Free Software Foundation, version 2.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
#  Mr. Pollard may be written at 112 Roberts Ln, Lansdale, PA  19446 USA
#  or e-mailed at <phil@crescendo.net>.

select((select(STDOUT),$|=1)[0]);

use Image::Magick;
use strict;

### Confuscate

my $debug = 1;

my $default_image  = 'images';
my $default_resize = 'resized';
my $default_size   = 100;
my $height_ratio   = 1.5; # What do you multiply width to get height

### Pragmata

my $pref_height = int( $default_size * $height_ratio );
my $pref_width  = $default_size;

my $imagedir = $default_image;

if (! -e $imagedir) { die "ERROR: Image directory $imagedir dosen't exist\n"; }
if (! -d $imagedir) { die "ERROR: $imagedir is not a directory\n"; }
if (! -r $imagedir) { die "ERROR: You do not have permissions to read from $imagedir\n"; }

my $thumbdir = $default_resize;

if (! -e $thumbdir) { print "WARN: Directory $thumbdir dosen't exist, creating.\n"; system("mkdir $thumbdir"); }
if (! -d $thumbdir) { die "ERROR: $thumbdir is not a directory\n"; }
if (! -w $thumbdir) { die "ERROR: You do not have permissions to write to $thumbdir\n"; }

my @files;

opendir IMAGES, $imagedir;
map { push @files, $_ if &is_image($_); } (readdir IMAGES);
closedir IMAGES;

sub numerically { $a <=> $b }
@files = sort numerically @files;

$debug && do { 
  print "\nProcessing ", scalar(@files), " files.\n\n";
  print "/---------------------------------------------------------------------\\\n";
  print "|         Filename         |   Start Size   |    End Size    | Status |\n";
  print "|--------------------------|----------------|----------------|--------|\n";
};

foreach my $file (@files) {
  my $in  = &clean($imagedir,$file);
  my $out = &clean($thumbdir,$file);

  chop $out; chop $out; chop $out;
  $out .= 'jpg';

  &makethumb($file,$in,$out);
}

### Fine

$debug && do { print "\\---------------------------------------------------------------------/\n\n"; };

### Submarines

sub clean {
  my $dir = join '/', @_;
     $dir =~ s/\/\/+/\//g;
  return $dir;
}

sub makethumb {
  my $name    = shift @_;
  my $infile  = shift @_;
  my $outfile = shift @_;

  $debug && do { 
    print  '|'; 
    printf "%25.25s", $name;
    print  ' | '; 
  };
  
  my $image = Image::Magick->new;
  my $ret = $image->Read($infile);

  $debug && $ret && do {
     printf "%31.31s", $ret;
     print " |  skip! |\n";
  };

  next if $ret;

  my $width  = $image->Get('width' );
  my $height = $image->Get('height');

  $debug && do {
    printf "%14.14s", "$width x $height"; 
    print  ' | ';
  };

  my $current_ratio = $height / $width;
  my ($new_height,$new_width);

  if ( $current_ratio > $height_ratio ) { # tall and narrow
    my $delta   = $pref_width / $width;
    $new_height = int($height * $delta);
    $new_width  = $pref_width;
  } elsif ( $height_ratio > $current_ratio ) { # Fat and wide
    my $delta   = $pref_height / $height;
    $new_height = $pref_height;
    $new_width  = int($width * $delta);
  } else { # perfect size
    $new_height = $pref_height;
    $new_width  = $pref_width;
  }

  $image->Scale(height=>$new_height,width=>$new_width);

  if ( $new_width != $pref_width ) {
    my $delta = $new_width - $pref_width;

    my $x1 = int($delta/2);
    my $x2 = $delta - $x1;

    $image->Crop( 'x' => $x1 );
    $image->Crop( 'x' => (-1 * $x2) );
  }

  if ( $new_height != $pref_height ) {
    my $delta = $new_height - $pref_height;

    my $y1 = int($delta/2);
    my $y2 = $delta - $y1;

    $image->Crop( 'y' => $y1 );
    $image->Crop( 'y' => (-1 * $y2) );
  }

  $width  = $image->Get('width' );
  $height = $image->Get('height');

  $debug && do { 
    printf "%14.14s", "$width x $height"; 
    print  ' | '; 
  };

  $image->Write($outfile);
  
  $debug && do { print " done! |\n"; };

  return ($width, $height);
}

sub is_image {
  my $file = shift @_;
  if ( $file =~ /.bmp$/i || $file =~ /.gif$/i || $file =~ /.jpg$/i ||
       $file =~ /.png$/i || $file =~ /.psd$/i ) { return 1 } else { return 0 }
}
