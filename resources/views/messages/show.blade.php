@extends('layouts.app')

@section('title', 'View Message')

@section('content')
<div class="px-4 sm:px-0">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
            <div class="flex items-center gap-3">
                <a href="{{ route('messages.inbox', [$userType, $userId]) }}"
                   class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                    </svg>
                </a>
                <h1 class="text-3xl font-bold text-gray-900">Message</h1>
            </div>
        </div>
        <div class="mt-4 sm:mt-0 flex space-x-3">
            <a href="{{ route('messages.compose', [$userType, $userId, 'reply_to' => $message->message_id]) }}"
               class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
                </svg>
                Reply
            </a>
            @if($message->sender_type === get_class($user) && $message->sender_id === ($userType === 'patient' ? $user->patient_id : $user->provider_id))
                <form action="{{ route('messages.destroy', [$userType, $userId, $message->message_id]) }}" method="POST"
                      onsubmit="return confirm('Are you sure you want to delete this message?');">
                    @csrf
                    @method('DELETE')
                    <button type="submit"
                            class="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                        Delete
                    </button>
                </form>
            @endif
        </div>
    </div>

    @if(session('success'))
        <div class="mb-6 bg-green-50 border-l-4 border-green-500 p-4">
            <p class="text-green-800">{{ session('success') }}</p>
        </div>
    @endif

    <!-- Message Thread -->
    <div class="space-y-6">
        <!-- Parent Message (if this is a reply) -->
        @if($message->parentMessage)
            <div class="bg-gray-50 border-2 border-gray-200 shadow sm:rounded-lg overflow-hidden">
                <div class="px-6 py-4 bg-gray-100 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm text-gray-600">Original Message</p>
                        </div>
                        <span class="text-xs text-gray-500">
                            {{ $message->parentMessage->created_at->format('M d, Y h:i A') }}
                        </span>
                    </div>
                </div>
                <div class="px-6 py-4">
                    <div class="mb-3">
                        <p class="text-sm text-gray-600">
                            <span class="font-medium">From:</span> {{ $message->parentMessage->sender ? $message->parentMessage->sender->full_name : 'Unknown' }}
                        </p>
                        <p class="text-sm text-gray-600">
                            <span class="font-medium">To:</span> {{ $message->parentMessage->recipient ? $message->parentMessage->recipient->full_name : 'Unknown' }}
                        </p>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-3">{{ $message->parentMessage->subject }}</h3>
                    <div class="prose prose-sm max-w-none">
                        <p class="text-gray-700 whitespace-pre-wrap">{{ $message->parentMessage->body }}</p>
                    </div>
                </div>
            </div>
        @endif

        <!-- Current Message -->
        <div class="bg-white border-2 border-blue-200 shadow-lg sm:rounded-lg overflow-hidden">
            <div class="px-6 py-4 bg-blue-50 border-b border-blue-200">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-blue-900">
                            {{ $message->parentMessage ? 'Reply' : 'Message' }}
                        </p>
                    </div>
                    <span class="text-xs text-gray-500">
                        {{ $message->created_at->format('M d, Y h:i A') }}
                    </span>
                </div>
            </div>
            <div class="px-6 py-4">
                <div class="mb-4 pb-4 border-b border-gray-200">
                    <p class="text-sm text-gray-600 mb-1">
                        <span class="font-medium">From:</span> {{ $message->sender ? $message->sender->full_name : 'Unknown' }}
                    </p>
                    <p class="text-sm text-gray-600">
                        <span class="font-medium">To:</span> {{ $message->recipient ? $message->recipient->full_name : 'Unknown' }}
                    </p>
                </div>
                <h2 class="text-2xl font-bold text-gray-900 mb-4">{{ $message->subject }}</h2>
                <div class="prose prose-sm max-w-none">
                    <p class="text-gray-800 whitespace-pre-wrap">{{ $message->body }}</p>
                </div>
                @if($message->is_read && $message->read_at)
                    <div class="mt-4 pt-4 border-t border-gray-200">
                        <p class="text-xs text-gray-500">
                            <span class="inline-flex items-center">
                                <svg class="w-4 h-4 mr-1 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                                </svg>
                                Read on {{ $message->read_at->format('M d, Y h:i A') }}
                            </span>
                        </p>
                    </div>
                @endif
            </div>
        </div>

        <!-- Replies -->
        @if($message->replies->count() > 0)
            <div class="mt-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Replies</h3>
                <div class="space-y-4">
                    @foreach($message->replies as $reply)
                        <div class="bg-white border-2 border-gray-200 shadow sm:rounded-lg overflow-hidden ml-8">
                            <div class="px-6 py-3 bg-gray-50 border-b border-gray-200">
                                <div class="flex items-center justify-between">
                                    <p class="text-sm text-gray-600">
                                        <span class="font-medium">From:</span> {{ $reply->sender ? $reply->sender->full_name : 'Unknown' }}
                                    </p>
                                    <span class="text-xs text-gray-500">
                                        {{ $reply->created_at->format('M d, Y h:i A') }}
                                    </span>
                                </div>
                            </div>
                            <div class="px-6 py-4">
                                <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ $reply->body }}</p>
                            </div>
                        </div>
                    @endforeach
                </div>
            </div>
        @endif
    </div>
</div>
@endsection
