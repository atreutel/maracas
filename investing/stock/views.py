from django.shortcuts import render
from django.http import HttpResponse
from . import mitools

# Create your views here.
def index(request) :
	return render(request, 'stock/home.html')

def search(request) :
	error = False
	if 'symbol' in request.GET:
		symbol = request.GET['symbol']
		if not symbol:
			error = True
		else:
			info = mitools.getCompanyFromSymbol(symbol)
			if not info:
				error = True
			else:
				name = info[0]
				cik = info[1]
				filings = mitools.getFilings(name,cik,4)
				return render(request, 'stock/search_result.html', {'symbol':symbol, 'name':name, 'cik':cik, 'filings': filings})

	return render(request, 'stock/search_result.html', {'error': error})