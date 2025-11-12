<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('billing_items', function (Blueprint $table) {
            $table->id('item_id');
            $table->unsignedBigInteger('billing_id');
            $table->string('service_code', 50);
            $table->string('service_description');
            $table->integer('quantity')->default(1);
            $table->decimal('unit_price', 10, 2);
            $table->decimal('total_price', 10, 2);
            $table->text('notes')->nullable();
            $table->timestamps();

            $table->foreign('billing_id')->references('billing_id')->on('billings')->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('billing_items');
    }
};
