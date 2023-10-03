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
    return 0;
}