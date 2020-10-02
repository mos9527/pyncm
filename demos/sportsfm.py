import pyncm

pyncm.login.LoginViaCellphone('-your phone number here-','-your password here-')

a = pyncm.miniprograms.sportsfm.GetCalculatedSportsFMStatus(10000,1000,3000,[26497879],15000,100)
# am fast
print(a)