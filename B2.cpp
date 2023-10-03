#include<iostream>
using namespace std;

int main() 
{
    int arr[10],n;
    cout<<"\nEnter length of the array : ";
    cin>>n;
    cout<<"\nEnter selling price of each day :";
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    int pro[10],bp=arr[0];
   
    for(int i=0;i<n;i++) {
        for(int j=1;j<n;j++){
            if(bp<arr[j]){
                pro[i]=arr[j]-bp;
            }
            
        }
    }
    int count=0;
    for(int i=0;i<n;i++)
    {
        if(pro[0] < pro[i])
        {
            pro[0]=pro[i];
        }
        // count=i;
    }
    cout<<"\nMaximun profit gained is "<<pro[0]<<" at day "<< count+1 << " at selling price "<<arr[count];
}