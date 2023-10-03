#include <iostream>
using namespace std;

int arr[10],n;

void merge(int ar[],int l,int h)
{
    int mid = (l+h)/2;

    int len1 = mid - l + 1;
    int len2 = h - mid;
   

    int *first = new int[len1];
    int *second = new int[len2];

    //copy values
    int mainArrayIndex = l;
    for(int i=0; i<len1; i++) {
        first[i] = ar[mainArrayIndex++];
        }

    mainArrayIndex = mid+1;
    for(int i=0; i<len2; i++) {
        second[i] = ar[mainArrayIndex++];
    }

    //merge 2 sorted arrays     
    int index1 = 0;
    int index2 = 0;
    mainArrayIndex = l;

    while(index1 < len1 && index2 < len2) {
        if(first[index1]!=0) {
            arr[mainArrayIndex++] = first[index1++];
        }
        else{
            arr[mainArrayIndex++] = second[index2++];
        }
    }   

    while(index1 < len1) {
        arr[mainArrayIndex++] = first[index1++];
    }

    while(index2 < len2 ) {
        arr[mainArrayIndex++] = second[index2++];
    }

    delete []first;
    delete []second;

}


void pushZerosToEnd(int ar[], int low, int high) {
    if (low < high) {
        int mid = (low + high) / 2;
        
        pushZerosToEnd(ar, low, mid);
        pushZerosToEnd(ar, mid + 1, high);
        
        //Merge
        merge(ar,low,high);
    }
}

int main() {
    cout<<"\nEnter number of elements:";
    cin>>n;
    cout<<"\nEnter elements of array: ";
    for(int i=0;i<n;i++)
    {
        cin>>arr[i];
    }

    pushZerosToEnd(arr, 0, n - 1);

   
    for (int i = 0; i < n; i++) {
       cout << arr[i] << " ";
    }
    
    
    return 0;
}
