from lxml import html
import requests
from urllib.request import urlopen
import xmltodict
from xml.dom import minidom
import xml.etree.ElementTree as ET

def getRequest(href):
    page = requests.get(href)
    return html.fromstring(page.content)

def getCompanyFromSymbol(symbol):
	tree = getRequest("https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + symbol)
	name = tree.xpath('//*[@class="companyName"]/text()')[0]
	cik = tree.xpath('//*[@class="companyName"]/a/text()')[0].split(' ')[0]
	result = []
	if name and cik:
		result = [name,cik]
	return result

def getFilings(name,cik,count):
	url = getFilingsUrl(cik, '10-K',count)
	tree = getRequest(url)
	filings = getReports(tree,count)
	return filings

def getFilingsUrl(cik, filetype, count):
	url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + cik + "&type=" + filetype + "&owner=include&count=" + str(count)
	return url

def buildFilings(tree, count=1):
	reports = getReports(tree, count)
	return reports
	#result = "<table><tr><td>Quarter</td><td>URL</td><td>Liabilities</td></tr>"
	#for report in reports:
	#	result += '<tr><td>' + str(report.quarter) + '</td><td>' + report.url + '</td><td>' + str(report.liabilities) + '</td></tr>'
	#result += '</table>'
	#return result

class filingsReport(object):
	url = ''

def getReports(tree, count=1):
	baseurl = "https://www.sec.gov"
	elems = tree.xpath('//*[@id="documentsbutton"]')[:count]
	result = []
	for elem in elems:
		url = baseurl + elem.attrib["href"]
		contentPage = getRequest(url)
		url = baseurl + contentPage.xpath('//*[@id="formDiv"]/div/table[@summary="Data Files"]/tr[2]/td[3]/a')[0].attrib["href"]
		dom = minidom.parse(urlopen(url))
		report = filingsReport()
		report.url = url
		report.fiscalYear = str(getReportedValue(dom,'dei:DocumentFiscalYearFocus'))
		report.fiscalPeriod = str(getReportedValue(dom,'dei:DocumentFiscalPeriodFocus'))
		report.period = report.fiscalPeriod + report.fiscalYear
		report.liabilities = getReportedValue(dom,'us-gaap:Liabilities')
		report.eps = getReportedValue(dom,'us-gaap:EarningsPerShareDiluted')
		#report.cash = getReportedValue(dom,'us-gaap:CashAndCashEquivalentsAtCarryingValue')
		report.cash = getReportedValue(dom,'us-gaap:CashCashEquivalentsAndShortTermInvestments')
		report.sales = getReportedValue(dom,'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax')
		report.shequity = getReportedValue(dom,'us-gaap:StockholdersEquity')
		report.shares = getReportedValue(dom,'us-gaap:CommonStockSharesOutstanding')
		if report.shequity and report.shares:
			report.bookvalue = int(report.shequity) / int(report.shares)
		else:
			report.bookvalue = 'Invalid'
		report.netincomeloss = getReportedValue(dom,'us-gaap:NetIncomeLoss')
		report.grossprofit = getReportedValue(dom,'us-gaap:GrossProfit')

		result.append(report)

	if len(result) == 1:
		return result[0]
	return result

def getReportedValue(rpt, elem):
	if not rpt.getElementsByTagName(elem):
		return
	return rpt.getElementsByTagName(elem)[0].firstChild.data