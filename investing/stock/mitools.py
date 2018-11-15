from lxml import html
import requests
from urllib.request import urlopen
from xml.dom import minidom
from bs4 import BeautifulSoup as soup


def getPage(url):
	client = urlopen(url)
	page = client.read()
	client.close()

	return soup(page, "html.parser")

def getRequest(href):
	page = requests.get(href)
	return html.fromstring(page.content)

def getCompanyFromSymbol(symbol):
	page_soup = getPage("https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + symbol)
	try:
		comp_name = page_soup.find(class_="companyName")
		name = [text for text in comp_name.stripped_strings][0]
		cik = comp_name.a.get_text().split(" ")[0]
		return [name,cik]
	except:
		return

def getFilings(name,cik,count):
	url = getFilingsUrl(cik, '10-K',count)
	page_soup = getPage(url)
	filings = getReports(page_soup,count)
	return filings

def getFilingsUrl(cik, filetype, count):
	url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + cik + "&type=" + filetype + "&owner=include&count=" + str(count)
	return url

def buildFilings(tree, count=1):
	reports = getReports(tree, count)
	return reports

class filingsReport(object):
	url = ''

def getReports(page_soup, count=1):
	baseurl = "https://www.sec.gov"
	elems = page_soup.find_all(id="documentsbutton", limit=count)
	result = []
	for elem in elems:
		url = baseurl + elem['href']
		index_page = getPage(url)
		url = baseurl + index_page.find(summary="Data Files").find_all('tr')[1].a['href']
		doc_soup = getDoc(url)
		#dom = minidom.parse(urlopen(url))
		report = filingsReport()
		report.url = url
		report.fiscalYear = str(getReportedValue(doc_soup,'dei:DocumentFiscalYearFocus'))
		report.fiscalPeriod = str(getReportedValue(doc_soup,'dei:DocumentFiscalPeriodFocus'))
		report.period = report.fiscalPeriod + report.fiscalYear
		report.liabilities = getReportedValue(doc_soup,'us-gaap:Liabilities')
		report.eps = getReportedValue(doc_soup,'us-gaap:EarningsPerShareDiluted')
		#report.cash = getReportedValue(doc_soup,'us-gaap:CashAndCashEquivalentsAtCarryingValue')
		report.cash = getReportedValue(doc_soup,'us-gaap:CashCashEquivalentsAndShortTermInvestments')
		report.sales = getReportedValue(doc_soup,'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax')
		report.shequity = getReportedValue(doc_soup,'us-gaap:StockholdersEquity')
		report.shares = getReportedValue(doc_soup,'us-gaap:CommonStockSharesOutstanding')
		if report.shequity and report.shares:
			report.bookvalue = int(report.shequity) / int(report.shares)
		else:
			report.bookvalue = 'Invalid'
		report.netincomeloss = getReportedValue(doc_soup,'us-gaap:NetIncomeLoss')
		report.grossprofit = getReportedValue(doc_soup,'us-gaap:GrossProfit')

		result.append(report)

	if len(result) == 1:
		return result[0]
	return result

def getDoc(url):
	client = urlopen(url)
	doc = client.read()
	client.close()

	return soup(doc, "xml")

def getReportedValue(rpt, elem):
	try:
		return rpt.find(elem).get_text()
	except:
		return