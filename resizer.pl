#!/usr/bin/perl 
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

use strict;

my @errors;

eval { require Image::Magick; } || push @errors, 'Image::Magick';
eval { require Term::Query;   } || push @errors, 'Term::Query';

if (@errors) {
  print "\nOOPS! - Required modules not found:\n\n";
  for my $next_trick (@errors) { print "             $next_trick\n"; }
  print "\nYou will need to install these modules.\nFor more information, ",
        "please read the documentation.\n\n";
  exit 1;
} else { 
  @errors = (); 
}

import Image::Magick;
import Term::Query 'query';

### Confuscate

my $debug = 1;

my $default_image  = 'images';
my $default_size   = 100;
my $default_resize = 'resized';

### Pragmata

my $imagedir = $default_image;

if (! -e $imagedir) { die "ERROR: Image directory $imagedir dosen't exist\n"; }
if (! -d $imagedir) { die "ERROR: $imagedir is not a directory\n"; }
if (! -r $imagedir) { die "ERROR: You do not have permissions to read from $imagedir\n"; }

my $thumbdir = $default_resize;

if (! -e $thumbdir) { print "WARN: Directory $thumbdir dosen't exist, creating.\n"; system("mkdir $thumbdir"); }
if (! -d $thumbdir) { die "ERROR: $thumbdir is not a directory\n"; }
if (! -w $thumbdir) { die "ERROR: You do not have permissions to write to $thumbdir\n"; }

my $pref_width = my $pref_height = $default_size;
my $upsize = 0;

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
  warn "$ret" if $ret;

  my $width  = $image->Get('width' );
  my $height = $image->Get('height');

  $debug && do {
    printf "%14.14s", "$width x $height"; 
    print  ' | ';
  };

  if ( $height <= $pref_height && $width <= $pref_width && $upsize == 0 ) {
    # Leave the size the same!
  } elsif ( $height > $width ) {
    my $newwidth = int (($pref_height / $height) * $width);
    $image->Scale(height=>$pref_height,width=>$newwidth);
  } else {
    my $newheight = int (($pref_width / $width) * $height);
    $image->Scale(height=>$newheight,width=>$pref_width);
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

