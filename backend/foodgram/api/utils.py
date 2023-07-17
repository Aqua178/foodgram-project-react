from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def create_favorite_cart(serial, request, pk=None):
    recipe = get_object_or_404(Recipe, pk=pk)
    serializer = serial(data=request.data,
                        context={'request': request,
                                 'pk': pk})
    if serializer.is_valid():
        serializer.save(recipe=recipe, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_favorite_cart(model, request, pk=None):
    get_object_or_404(model, recipe_id=pk, user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def get_author(request):
    return request.parser_context.get('kwargs').get('pk')


def generate_cart(queryset):
    msg = ''
    for item in queryset:
        msg += (f'{item["ingredient__name"]}, '
                f'({item["ingredient__measurement_unit"]}) '
                f'{item["total"]}') + '\n'
    response = HttpResponse(msg, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename=foodgram_products.txt')
    return response
