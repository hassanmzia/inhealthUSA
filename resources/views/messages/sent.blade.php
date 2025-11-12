@extends('layouts.app')

@section('title', 'Sent Messages')

@section('content')
<div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <div class="flex items-center gap-3">
                <a href="{{ $userType === 'patient' ? route('patients.show', $userId) : route('physicians.show', $userId) }}"
                   class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                    </svg>
                </a>
                <h1 class="text-3xl font-bold text-gray-900">Sent Messages</h1>
            </div>
            <p class="mt-2 text-sm text-gray-700">
                User: <span class="font-medium">{{ $user->full_name }}</span>
            </p>
        </div>
        <div class="mt-4 sm:mt-0 flex space-x-3">
            <a href="{{ route('messages.inbox', [$userType, $userId]) }}"
               class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                Inbox
            </a>
            <a href="{{ route('messages.compose', [$userType, $userId]) }}"
               class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-medical-blue hover:bg-blue-700">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Compose Message
            </a>
        </div>
    </div>

    @if(session('success'))
        <div class="mb-6 bg-green-50 border-l-4 border-green-500 p-4">
            <p class="text-green-800">{{ session('success') }}</p>
        </div>
    @endif

    <!-- Messages List -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <ul class="divide-y divide-gray-200">
            @forelse($messages as $message)
                <li>
                    <a href="{{ route('messages.show', [$userType, $userId, $message->message_id]) }}"
                       class="block hover:bg-gray-50 transition-colors">
                        <div class="px-6 py-4">
                            <div class="flex items-center justify-between">
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center justify-between">
                                        <p class="text-sm font-medium text-gray-900">
                                            To: {{ $message->recipient ? $message->recipient->full_name : 'Unknown' }}
                                        </p>
                                        <p class="text-xs text-gray-500">
                                            {{ $message->created_at->diffForHumans() }}
                                        </p>
                                    </div>
                                    <p class="text-sm text-gray-900 mt-1 font-medium">
                                        {{ $message->subject }}
                                    </p>
                                    <p class="text-sm text-gray-600 mt-1 truncate">
                                        {{ Str::limit(strip_tags($message->body), 100) }}
                                    </p>
                                    @if($message->is_read)
                                        <div class="mt-2">
                                            <span class="inline-flex items-center px-2 py-1 text-xs font-medium text-green-800 bg-green-100 rounded-full">
                                                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                                                </svg>
                                                Read
                                            </span>
                                        </div>
                                    @endif
                                </div>
                                <div class="ml-4">
                                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </a>
                </li>
            @empty
                <li class="px-6 py-12 text-center">
                    <div class="mx-auto h-16 w-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                        <svg class="h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                        </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">No sent messages</h3>
                    <p class="text-gray-600">You haven't sent any messages yet</p>
                </li>
            @endforelse
        </ul>
    </div>

    <!-- Pagination -->
    @if($messages->hasPages())
        <div class="mt-6">
            {{ $messages->links() }}
        </div>
    @endif
</div>
@endsection
