# GeoLocation lookup using DNS DL server (instead of Geo IP)
# http://www.netop.org/geoip.html
# Requires dnspython: http://www.dnspython.org
import dns.resolver

dnsdlserver = 'country.netop.org'
ip = '86.24.0.80'
iploc = None

if len(ip) <= 15:
   # IPv4 IP Address
   iplist = ip.split('.')
   iprev = iplist
   iprev.reverse()
elif len(ip) > 15:
   # IPv6 IP Address
   iplist = ip.split(':')
   iprev = iplist
   iprev.reverse()

# Form into domain string for the lookup
dnsdlrequest = '.'.join(iprev) + '.' + dnsdlserver

# Get the TXT string in which should be embeded a country code
dnsdlresults = dns.resolver.query(dnsdlrequest, 'TXT')

# Extract the country code
for rdata in dnsdlresults:
    iploc = rdata

print iploc