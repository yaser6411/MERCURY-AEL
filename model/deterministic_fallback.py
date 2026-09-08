"""Offline deterministic fallback algorithm pool."""
import random
from typing import Dict, Optional


class DeterministicFallback:
    """Deterministic algorithm pool for offline operation."""

    # Sorted algorithms (deterministic fallback)
    SORT_ALGORITHMS = [
        # Bubble sort variant 1
        '''
def bubble_sort(arr):
    """Bubble sort implementation."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
''',
        # Bubble sort variant 2 (optimized)
        '''
def bubble_sort_optimized(arr):
    """Optimized bubble sort with early termination."""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
''',
        # Insertion sort
        '''
def insertion_sort(arr):
    """Insertion sort implementation."""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
''',
    ]

    # Search algorithms
    SEARCH_ALGORITHMS = [
        # Linear search
        '''
def linear_search(arr, target):
    """Linear search implementation."""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
''',
        # Binary search
        '''
def binary_search(arr, target):
    """Binary search implementation."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
''',
    ]

    # Utility algorithms
    UTILITY_ALGORITHMS = [
        # Fibonacci
        '''
def fibonacci(n):
    """Fibonacci sequence generator."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
''',
        # Prime checker
        '''
def is_prime(n):
    """Check if number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True
''',
    ]

    ALGORITHM_POOL = {
        'sort': SORT_ALGORITHMS,
        'search': SEARCH_ALGORITHMS,
        'utility': UTILITY_ALGORITHMS,
        'generic': SORT_ALGORITHMS + SEARCH_ALGORITHMS + UTILITY_ALGORITHMS
    }

    def __init__(self):
        self.category_counter = {}

    def generate(self, context: Optional[Dict] = None) -> str:
        """Return candidate from deterministic pool.
        
        Args:
            context: Optional context dictionary with 'category' key
            
        Returns:
            Algorithm source code as string
        """
        context = context or {}
        category = context.get('category', 'generic')
        
        # Get pool for category
        pool = self.ALGORITHM_POOL.get(category, self.ALGORITHM_POOL['generic'])
        
        if pool:
            # Select deterministically based on generation count
            generation = context.get('generation', 0)
            idx = generation % len(pool)
            return pool[idx]
        
        return self.generic_algorithm()

    @staticmethod
    def generic_algorithm() -> str:
        """Generic fallback algorithm."""
        return '''
def generic_function(data):
    """Generic placeholder function."""
    if isinstance(data, list):
        return sorted(data)
    return data
'''
