from logger import logger
from .models import products, ProductStars, ProductInCart
from rest_framework.views import APIView
from rest_framework.response import Response

class get_products(APIView):
    def get(self, request):
        try:
            n = request.query_params.get('n', None)
            product_id = request.query_params.get("id", None)

            if n != None :
                n = int(n)
                product_qs = products.objects.all()[n*6:(n+1)*6]
            
            elif product_id != None :
                product_id = int(product_id)
                product_qs = products.objects.filter(id=product_id)
            
            else :
                product_qs = products.objects.all()

            data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.discription,
                    "price": p.price,
                    "currency_type": p.currency_type,
                    "image": p.image.url if p.image else None,
                    "stars": p.stars if p.stars else 0,
                }
                for p in product_qs
            ]

            return Response({"products": data})
        
        except Exception as e:
            logger.error(f"error in get_products: {e}")
            return Response({"products": False}, status=200)

class HasUserStarredProduct(APIView):
    def get(self, request):
        try:
            prd_id = request.query_params.get('prd_ID')
            user = request.user
            if user.is_authenticated:
                if not prd_id:
                    return Response({"has_starred": "ERROR", "error": "prd_ID parameter is required"}, status=400)
                
                try:
                    prd_id = int(prd_id)
                except:
                    return Response({"has_starred": "ERROR", "error": "Invalid product ID !"}, status=400)

                if not products.objects.filter(id=prd_id).exists():
                    return Response({"has_starred": "ERROR", "error": "Invalid product !"}, status=404)

                has_starred = ProductStars.objects.filter(product_id=prd_id, user=user).exists()

                return Response({"has_starred": has_starred})
            
            return Response({"has_starred": "NO_LOGIN", "msg":"Login required !"}, status=401)
        
        except Exception as e:
            logger.error(f"error in HasUserStarredProduct: {e}")
            return Response({"has_starred": "ERROR"}, status=500)

class ChangeStar(APIView):
    def post(self, request):
        try:
            prd_id = request.query_params.get("prd_ID")
            opt = request.query_params.get("opt")
            user = request.user

            if user.is_authenticated:
                if prd_id is None:
                    return Response({"status": "ERROR", "msg": "prd_ID parameter is required"}, status=400)
                if opt not in ["ADD", "DEL"]:
                    return Response({"status": "ERROR", "msg": "The value of opt is not correct"}, status=400)
                
                try:
                    prd_id = int(prd_id)
                except:
                    return Response({"status": "ERROR", "msg": "Invalid Product ID."}, status=400)

                try:
                    product = products.objects.get(id=prd_id)
                except products.DoesNotExist:
                    return Response({"status": "ERROR", "msg": "Product not found."}, status=404)


                if opt == "ADD":
                    obj, created = ProductStars.objects.get_or_create(user=user, product=product)
                    if created:
                        product.stars += 1
                        product.save()
                        return Response({"status": "OK", "msg": "Star added."}, status=200)
                    else:
                        return Response({"status": "ERROR", "msg": "Already starred."}, status=400)

                elif opt == "DEL":
                    deleted, _ = ProductStars.objects.filter(user=user, product=product).delete()
                    if deleted:
                        product.stars = max(product.stars - 1, 0)
                        product.save()
                        return Response({"status": "OK", "msg": "Star removed."})
                    else:
                        return Response({"status": "ERROR", "msg": "No star to remove."}, status=400)
            
            return Response({"status": "NO_LOGIN", "msg": "Login required to rate products !"}, status=401)
        
        except Exception as e:
            return Response({"status": "ERROR", "msg": str(e)}, status=500)

class isProductInCart(APIView):
    def get(self, request):
        try:
            prd_id = request.query_params.get('prd_ID')
            user = request.user
            if user.is_authenticated:
                if not prd_id:
                    return Response({"status": "ERROR", "error": "prd_ID parameter is required"}, status=400)
                
                try:
                    prd_id = int(prd_id)
                except:
                    return Response({"status": "ERROR", "error": "Invalid product ID !"}, status=400)

                if not products.objects.filter(id=prd_id).exists():
                    return Response({"status": "ERROR", "error": "Invalid product !"}, status=404)

                status = ProductInCart.objects.filter(product_id=prd_id, user=user).exists()

                return Response({"status": status})
            
            return Response({"status": "NO_LOGIN", "error":"Login required !"}, status=401)
        
        except Exception as e:
            logger.error(f"error in HasUserStarredProduct: {e}")
            return Response({"status": "ERROR"}, status=500)

class ChangeInCart(APIView):
    def post(self, request):
        try:
            prd_id = request.query_params.get("prd_ID")
            opt = request.query_params.get("opt")
            user = request.user

            if user.is_authenticated:
                if prd_id is None:
                    return Response({"status": "ERROR", "msg": "prd_ID parameter is required"}, status=400)
                if opt not in ["ADD", "DEL"]:
                    return Response({"status": "ERROR", "msg": "Invalid parameters. The value of opt is not correct"}, status=400)
                
                try:
                    prd_id = int(prd_id)
                except:
                    return Response({"status": "ERROR", "msg": "Invalid Product ID. Your prd_ID has incorrect type !"}, status=400)

                try:
                    product = products.objects.get(id=prd_id)
                except products.DoesNotExist:
                    return Response({"status": "ERROR", "msg": "Product not found."}, status=404)


                if opt == "ADD":
                    obj, created = ProductInCart.objects.get_or_create(user=user, product=product)
                    if created:
                        return Response({"status": "OK", "msg": "Added to cart"}, status=200)
                    else:
                        return Response({"status": "ERROR", "msg": "Your product already is in the cart ."}, status=400)

                elif opt == "DEL":
                    deleted, _ = ProductInCart.objects.filter(user=user, product=product).delete()
                    if deleted:
                        return Response({"status": "OK", "msg": "product removed from the cart"})
                    else:
                        return Response({"status": "ERROR", "msg": "This Product is not in the cart ! so you can't remove it."}, status=400)
            
            return Response({"status": "NO_LOGIN", "msg": "Login required to rate products !"}, status=401)
        
        except Exception as e:
            return Response({"status": "ERROR", "msg": str(e)}, status=500)

 
        