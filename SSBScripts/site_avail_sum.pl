#!/usr/bin/perl -w

# Program to generate a text file with the site availabilities for the SSB
#
#   Input: none
#   Writes the lists to files in the current directory
#

use LWP::Simple;
use XML::Parser;
use File::Temp("tempfile");

# Small class for Sites

package Site;

sub new {
    my $class = shift;
    my $id = shift;
    my $self = {ID => $id, CMS => '', SAM => ''};
    bless $self, $class;
}

sub tier {
    my $self = shift;
    return substr $self->{CMS}, 1, 1;
}

# Main program

package main;

# Array with all Sites and tiers
%sites = ();

#Get XML file from SiteDB

my $url = "https://cmsweb.cern.ch/sitedb/sitedb/reports/showXMLReport/?reportid=naming_convention.ini";
my $doc = get($url) or die "Cannot retrieve XML\n";
my $filepath = "/afs/cern.ch/cms/LCG/SiteComm/site_avail_sum.txt";
($fh, $tmpfile) = tempfile(UNLINK => 1) or die "Cannot create temporary file\n";

# Parse XML

$p = new XML::Parser(Handlers => {Start => \&h_start, Char  => \&h_char});
$p->parse($doc) or die "Cannot parse XML\n";

# Exit if no sites are found

if (! %sites) {
    die "No sites found!\n";
}

%seen = ();

foreach my $s ( values %sites ) {
    my $cms = $s->{CMS};
    next if $seen{$cms}++;
    my $t = $s->tier;
    next if ( $t eq 'X' );
# Skip T[01]_CH_CERN
    next if ($s->{CMS} eq 'T0_CH_CERN');
    next if ($s->{CMS} eq 'T1_CH_CERN');
    my $timestamp = &timestamp;
    my $avail = &get_avail($s->{CMS});
    die "Cannot get XML\n" if ($avail eq 'error');
    next if ( $avail eq 'NA' );
    my $colour = 'green';
    if ( $t == 0 or $t == 1 ) {
	$colour = 'red' if ( $avail ne 'NA' and $avail < 90 );
    } elsif ( $t == 2 ) {
	$colour = 'red' if ( $avail ne 'NA' and $avail < 80 );
    }
    $colour = 'red' if ( $avail eq 'NA' );
    my $comm_url = &avail_url($s->{CMS});
    printf $fh "%s\t%s\t%s\t%s\t%s\n", $timestamp, $s->{CMS}, "${avail}",
    $colour, $comm_url;
} 
close $fh;
system("/bin/cp -f $tmpfile $filepath"); 

# Handler routines

sub h_start {
    my $p = shift;
    my $el = shift;
    my %attr = ();
    while (@_) {
	my $a = shift;
	my $v = shift;
	$attr{$a} = $v;
    }
    if ($el eq 'item') {
	$lastid = $attr{id};
	my $s = new Site($attr{id});
	$sites{$lastid} = $s;
    }
}

sub h_char {
    my $p = shift;
    my $a = shift;

    if ($p->in_element('cms')) {
	my $site = $sites{$lastid};
	$site->{CMS} = $a; 
    }
    if ($p->in_element('sam')) {
	my $site = $sites{$lastid};
	$site->{SAM} = $a; 
    }
}

sub timestamp {

    my @time = gmtime(time);
    my $timestamp = sprintf("%s-%02d-%02d %02d:%02d:%02d",
			    1900 + $time[5],
			    1 + $time[4],
			    $time[3],
			    $time[2],
			    $time[1],
			    $time[0]
			    );
    return $timestamp;
}

sub ptime {

    my @time = @_;
    my $t = sprintf("%s-%02d-%02d",
			1900 + $time[5], 1 + $time[4], $time[3]);
    return $t;
}

sub get_avail {

    my $site = shift;
    my $avail = 'NA';
    my $url = "http://dashb-cms-sum.cern.ch/dashboard/request.py/getAvailabilityResults?profile_name=CMS_CRITICAL_FULL&view=siteavl&time_range=last24&plot_type=ranking&group_name=${site}";
    my $cmd = "curl -H \'Accept: text/xml\' \'$url\' 2> /dev/null";
    open(SUM,"$cmd | xmllint --format - |") or warn 'Cannot query SUM\n';
    my $a = '';
    while (<SUM>) {
	chomp;
	if (/<item>(\d*\.+\d*)<\/item>/) {
	    $avail = sprintf "%.3f", $1;
            $avail = $avail * 100.;
	}
    }
    return $avail;
}

sub avail_url {

    my $site = shift;
    my $start = &ptime(gmtime(time));
    my $end = &ptime(gmtime(time+86400));
    my $url = "http://dashb-cms-sum.cern.ch/dashboard/request.py/historicalsmryview-sum#view=siteavl&time%5B%5D=individual&starttime=$start&endtime=$end&profile=CMS_CRITICAL_FULL&group=AllGroups&site%5B%5D=$site&type=quality";
    return $url;
}
