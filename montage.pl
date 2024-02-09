#!/usr/bin/perl

use Tk;
use strict;

my $mw = MainWindow->new();
$mw->withdraw;

$mw->geometry('800x600+25+25');
$mw->title('Image Montage');

my $info = 'Version ' . (split ' ', '$Revision: 1.2 $')[1] . ' Copyright 1999-2006, Phillip Pollard';

my $logo  = $mw->Photo( -file=> 'app/logosm.gif' );
my $blank = $mw->Photo( -file=> 'app/blank.gif'  );

my $head = $mw->Frame();
my $main = $mw->Frame();
my $foot = $mw->Frame();

# Menu bar

my $mbar = $mw -> Menu();
$mw->configure(-menu => $mbar);

my $file = $mbar -> cascade(-label=>"File", -underline=>0, -tearoff => 0);
$file->command(-label => "About", -underline=>0, -command=> \&do_about );
$file->separator();
$file->command(-label =>"Exit", -underline=>1, -command => \&do_exit );

#my $edit = $mbar -> cascade(-label=>"Edit", -underline=>0, -tearoff => 0);
#$edit->command(-label => "Breeds", -underline=>0, -command=> \&do_edit_breeds );
#$edit->command(-label => "Medical Conditions", -underline=>0, -command=> \&do_edit_medical );
#$edit->command(-label => "Vaccines", -underline=>0, -command=> \&do_edit_vaccines );
#$edit->command(-label => "Breeders", -underline=>1, -command=> \&do_edit_breeders );

# Main body frame

$head->Label(-image=>$blank)->pack(-side=>'left');
$head->Label(-image=>$blank)->pack(-side=>'right');

# Footer frame

$foot->Label( -textvariable=>\$info, -relief=>'ridge', -anchor=>'w')
     ->pack( -side=>'bottom', -anchor=>'w', -fill=>'x');

# Pack the window

$head->pack( -side=> 'top'    , -anchor=> 'w', -expand=>1, -fill=>'both' );
$foot->pack( -side=> 'bottom' , -anchor=> 'w'     , -fill=>'x' );
$main->pack( -side=> 'left'   , -anchor=> 'n', -expand=>1, -fill=>'both' );

&debug("Entering MainLoop();");

$mw->deiconify;

MainLoop();

### Page

sub do_about {
  &debug("Page: do_about();");

  my $message = "Image Montage\n\n$info";
  $message =~ s/ - /\n/g;

  my $dialog = $mw->Dialog(-title=>'About Montage', -text=>$message, -image=>$logo, -background=>'#FFFFFF');
  my $respose = $dialog->Show();
  $dialog->destroy() if Tk::Exists($dialog);
}

sub do_exit {
  &debug("Page: do_exit();");
  $mw->destroy();
}

### Subroutines

sub debug {
  for my $line (@_) {
    my $chunk = $line;
    chomp $chunk;
    print STDERR "DEBUG: $chunk\n";
  }
}
