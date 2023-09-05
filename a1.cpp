#include<iostream>
using namespace std;


int main()
{
  int a[10],i,n,mid=0,l=0,h=0,temp,count=0;
  cout<<"Enter the number of elements: ";
  cin>>n;
  cout<<"\nEnter elements:";
  for(i=0;i<n;i++)
  {
    cin>>a[i];
  }
  h = n - 1;
  while(h>=l)
  {
    mid= (l+h)/2;
    if(a[mid]==0)
    {
      h=mid-1;
    }
    else if(a[mid]==1)
    {
      l=mid+1;
    }
    if(a[mid]==0 && (a[mid-1]==1 && a[mid+1]==0))
    {
      temp=mid;
    }
  }
  count=n-temp;
  cout<<"\nNUmber of zeroes : "<<count;
}