from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.views import generic
from django.template.context_processors import csrf
from mymail.models import user, mailing, trash, sent_mai
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt



def home(request):
	return render(request, 'create_account.html')

def registered(request):
	f_name = request.POST.get('f_name')
	l_name =  request.POST.get('l_name')
	mail = request.POST.get('mail')
	userid = request.POST.get('user_name')
	gender = request.POST.get('optionsRadios')
	password = request.POST.get('password')

	if not user.objects.filter(Q(user_id=userid) | Q(email=mail)):
		obj = user(first_name = f_name,last_name=l_name,email=mail,user_id=userid,gender=gender,password=password)
		obj.save()
		return render_to_response('registration.html', {},context_instance=RequestContext(request))
	else:
		html = '<html><body><h1>Error UserName already exists</h1><br>click <a href="/../mymail">here</a> to Register</body></html>'
		return HttpResponse(html)

def user_validate(request):
	userid = request.POST.get('userid')
	password = request.POST.get('pwd')
	try:
		us = user.objects.get(user_id=userid)
	except user.DoesNotExist:
		return HttpResponseRedirect('/../mymail/')
	if us is not None:
		if us.password == password:
			request.session["user_id"] = userid 
			print request.session["user_id"]
			i = user.objects.get(user_id=request.session["user_id"])
			u = mailing.objects.filter(receiver_id=i.id)
			return HttpResponseRedirect('/../mymail/success/inbox/')
		else:
			return HttpResponseRedirect('/../mymail/')
	else:
		return HttpResponseRedirect('/../mymail/')

def success_login(request):
	return render(request,'success.html')
def new_mail(request):
		return render(request,'new_mail.html')
def sending(request,p):
	sent_from = request.session["user_id"]
	sent_to = request.POST.get('to')
	subj = request.POST.get('subject')
	content = request.POST.get('content')
	try:
		use = user.objects.get(user_id=sent_to)
	except user.DoesNotExist:
		return HttpResponseRedirect('../new_mail')
	if use is not None:
		m = mailing(sender=user.objects.get(user_id=sent_from),receiver=user.objects.get(user_id=sent_to),subject=subj,messege=content)
		n = sent_mai(sende=user.objects.get(user_id=sent_from),receive=user.objects.get(user_id=sent_to),subject=subj,messege=content)
		m.save()
		n.save()
		return HttpResponseRedirect('/mymail/success/'+p+'/')
def inbox_mail(request):
	i = user.objects.get(user_id=request.session["user_id"])
	u = mailing.objects.filter(receiver_id=i.id)
	return render(request,'inbox.html',{'u':u})
def sent_mail(request):
	i = user.objects.get(user_id=request.session["user_id"])
	u = sent_mai.objects.filter(sende_id=i.id)
	return render(request,'sent.html',{'u':u})
	
def trash_mail(request):
	i = trash.objects.filter(Q(sender=request.session["user_id"]) | Q(receiver=request.session["user_id"]))
	return render(request,'trash.html',{'u':i})
def displaying(request, box,mail_id):
	if box == 'inbox':
		msg = mailing.objects.get(id=mail_id)
		msg.visited=True
		msg.save()
		msg = mailing.objects.get(id=mail_id)
		return render(request,'display.html',{'msg':msg})
	elif box == 'sentmail':
		ms = sent_mai.objects.get(id=mail_id)
		return render(request,'display.html',{'msg':ms})
	elif box == 'trash':
		msgg = trash.objects.get(m_id=mail_id)
		return render(request,'display.html',{'msg':msgg})

def logout(request):
	del request.session["user_id"]
	return HttpResponseRedirect('/mymail/')
def trashing(request,box,mail_id):
	if box == 'inbox':
		i = mailing.objects.get(id=mail_id)
		if not trash.objects.filter(m_id = i.id):
			o = trash(m_id=i.id,sender=user.objects.get(id=i.sender_id).user_id,receiver=user.objects.get(id=i.receiver_id).user_id,messege=i.messege,subject=i.subject)
			o.save()
		i.delete()
		return HttpResponseRedirect('../../')
	elif box == 'sentmail':
		i = sent_mai.objects.get(id=mail_id)
		if not trash.objects.filter(m_id = i.id):
			o = trash(m_id=i.id,sender=user.objects.get(id=i.sende_id).user_id,receiver=user.objects.get(id=i.receive_id).user_id,messege=i.messege,subject=i.subject)
			o.save()
		i.delete()
		return HttpResponseRedirect('../../')
	elif box =='trash':
		i = trash.objects.get(m_id=mail_id)
		i.delete()
		return HttpResponseRedirect('../../')
@csrf_exempt
def check(request):
	userid = request.POST.get('userid')
	if not user.objects.filter(user_id = userid):
		return HttpResponse('0')
	else:
		return HttpResponse('1')

@csrf_exempt
def checki(request):
	mail = request.POST.get('email')
	if not user.objects.filter(email = mail):
		return HttpResponse('0')
	else:
		return HttpResponse('1')