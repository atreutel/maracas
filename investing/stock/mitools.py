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

def getCompanyFromSymbol(symbol):
	page_soup = getPage("https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + symbol)
	try:
		company = companyResult()
		comp_name = page_soup.find(class_="companyName")
		company.symbol = symbol
		company.name = [text for text in comp_name.stripped_strings][0]
		company.cik = comp_name.a.get_text().split(" ")[0]
		getFilings(company,3)
		return company
	except:
		return

def getFilings(company,count):
	company.filingsquery = getFilingsUrl(company.cik, '10-K',count)
	page_soup = getPage(company.filingsquery)
	getReports(company,page_soup,count)
	return

def getFilingsUrl(cik, filetype, count):
	url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + cik + "&type=" + filetype + "&owner=include&count=" + str(count)
	return url

class filingsReport(object):
	url = ''

class companyResult(object):
	name = ''
	cik = ''

def getReports(company, page_soup, count=1):
	try:
		baseurl = "https://www.sec.gov"
		elems = page_soup.find_all(id="documentsbutton", limit=count)
		company.reports = []
		for elem in elems:
			try:
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

				company.reports.append(report)
			except:
				continue

		return
	except:
		return

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