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
			company = mitools.getCompanyFromSymbol(symbol)
			if not company:
				error = True
			else:
				return render(request, 'stock/search_result.html', {'company':company})

	return render(request, 'stock/search_result.html', {'error': error})