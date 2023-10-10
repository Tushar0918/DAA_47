#include<iostream>
using namespace std;

int largest(int arr[], int n)
{
    int i;
    int max = arr[0];
    for (i = 1; i < n; i++)
        if (arr[i] > max)
            max = arr[i];
    return max;
}

int main() 
{
    int arr[10],n,i,max,ele;
    cout<<"\nEnter length of the array : ";
    cin>>n;
    cout<<"\nEnter selling price of each day :";
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    max = largest(arr,n);
    cout<<max;
    i = 0;
    while (i < n)
    {
        if (arr[i] == max) {
            break;
        }
        i++;
    }
    int res[10],mp=0;
    for(int j=0;j<i;j++){
        res[j]= max - arr[j];
    }
    for(int j=0;j<i;j++) {
        mp = mp + res[j];
    }
    cout<<"\nMAximum profit gained is "<<mp<<" on day"<<i+1;
    return 0;   
}