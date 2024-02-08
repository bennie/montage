#!/usr/bin/env perl

use Data::UUID;
use File::Find;
use Image::Magick;
use strict;

### Config

my $debug = 1;

my $default_image  = 'images';
my $default_resize = 'resized';
my $default_size   = 100;
my $height_ratio   = 1.5; # What do you multiply width to get height
my $thumbnail_type = 'png';

### Main

select((select(STDOUT),$|=1)[0]);

my $ug = Data::UUID->new;

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

$debug && do {
  print "/-----------------------------------------------------------------------------\\\n";
  print "|        Filename         |  Start Size  |  End Size   |         Status        |\n";
  print "|-------------------------|--------------|-------------|-----------------------|\n";
};

sub handle_file {
	my $in = $File::Find::name;
	return unless &is_image($in);

    my $uuid = $ug->create_from_name_str(NameSpace_OID, $in);
	my $out = &clean($thumbdir,$uuid.'.'.$thumbnail_type);
	
	&makethumb($_,$in,$out);
}
find({ wanted => \&handle_file, no_chdir=>1}, $default_image);

### Fine

$debug && do { print "\\-----------------------------------------------------------------------------/\n\n"; };

### Subroutines

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
    printf "%25s", substr($name, -25);
    print  '|';
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
    printf "%13.13s", $width.'x'.$height;
    print  ' |';
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
    printf "%9.9s", $width.'x'.$height;
    print  ' |';
  };

  $image->Write($outfile);

  $debug && do {
    printf "%25.25s", substr($outfile, -25);
    print "|\n";
  };

  return ($width, $height);
}

sub is_image {
  my $file = shift @_;
  if ( $file =~ /.bmp$/i || $file =~ /.gif$/i || $file =~ /.jpg$/i ||
       $file =~ /.png$/i || $file =~ /.psd$/i ) { return 1 } else { return 0 }
}
