def interest(n, months, z=500):
    z = z/94
    print(z, "-> Starting point") 
    for i in range(n):
        z*=2
        print(z,"->",months[i])

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
interest(12,months)