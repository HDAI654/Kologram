from logger import logger
from .models import products, ProductStars, ProductInCart, ProductLikes, ProductComment
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .forms import add_prd, edit_prd

class get_products(APIView):
    def get(self, request):
        try:
            page = request.query_params.get('page', None)
            product_id = request.query_params.get("id", None)
            by_user = request.query_params.get("by_user", None)

            if page != None :
                page = int(page)
                search_sts = request.query_params.get('search', "0")

                if search_sts == "0" or search_sts == None:
                    product_qs = products.objects.all()[page*6:(page+1)*6] 
                else:
                    search_sts = str(search_sts)
                    if search_sts != "1":
                        return Response({"products": False, "error": "search parameter is invalid"}, status=400)
                    search_text = request.query_params.get('search_text', None)
                    if search_text == None:
                        return Response({"products": False, "error": "search_text parameter is required to search"}, status=400)
                    search_text = str(search_text)
                    product_qs = products.objects.filter(Q(name__icontains=search_text) | Q(discription__icontains=search_text))[page*6:(page+1)*6]
            
            elif product_id != None :
                product_id = int(product_id)
                product_qs = products.objects.filter(id=product_id)
            
            elif by_user != None :
                product_qs = products.objects.filter(user=request.user)

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
                    "likes": p.likes if p.likes else 0,
                    "condition": p.condition,
                }
                for p in product_qs
            ]

            return Response({"products": data})
        
        except Exception as e:
            logger.error(f"error in get_products: {e}")
            return Response({"products": False}, status=500)

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
            logger.error(f"Error in ChangeStar : {e}")
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
            logger.error(f"error in isProductInCart: {e}")
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
            logger.error(f"Error in ChangeInCart : {e}")
            return Response({"status": "ERROR", "msg": str(e)}, status=500)

class HasUserLikedProduct(APIView):
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

                status = ProductLikes.objects.filter(product_id=prd_id, user=user).exists()

                return Response({"status": status})
            
            return Response({"status": "NO_LOGIN", "msg":"Login required !"}, status=401)
        
        except Exception as e:
            logger.error(f"error in HasUserLikedProduct: {e}")
            return Response({"status": "ERROR"}, status=500)

class ChangeLike(APIView):
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
                    obj, created = ProductLikes.objects.get_or_create(user=user, product=product)
                    if created:
                        product.likes += 1
                        product.save()
                        return Response({"status": "OK", "msg": "Star added."}, status=200)
                    else:
                        return Response({"status": "ERROR", "msg": "Already starred."}, status=400)

                elif opt == "DEL":
                    deleted, _ = ProductLikes.objects.filter(user=user, product=product).delete()
                    if deleted:
                        product.likes = max(product.stars - 1, 0)
                        product.save()
                        return Response({"status": "OK", "msg": "Star removed."})
                    else:
                        return Response({"status": "ERROR", "msg": "No star to remove."}, status=400)
            
            return Response({"status": "NO_LOGIN", "msg": "Login required to rate products !"}, status=401)
        
        except Exception as e:
            logger.error(f"error in ChangeLike: {e}")
            return Response({"status": "ERROR", "msg": str(e)}, status=500)

class AddPrd(APIView):
    def post(self, request):
        try:
            form = add_prd(request.POST, request.FILES)
            if form.is_valid():
                if request.user.is_authenticated:
                    user = request.user
                    name = form.cleaned_data["name"]
                    discription = form.cleaned_data["discription"]
                    price = int(form.cleaned_data["price"])
                    currency_type = form.cleaned_data["currency_type"]
                    image = form.cleaned_data["image"]
                    condition = form.cleaned_data["condition"]

                    prd = products.objects.create(user=user, name=name, discription=discription, price=price, currency_type=currency_type, image=image, condition=condition)
                    prd.save()
                    return Response({"result":True}, status=200)
                
                return Response({"result":False, "error":"Login required to add a product !"}, status=401)
            
            return Response({"result":False, "error":"Invalid Data !"}, status=400)
        except Exception as e:
            logger.error(f"error in AddPrd: {e}")
            return Response({"result":False}, status=500)
 
class DelPrd(APIView):
    def post(self, request):
        try:
            id = request.data.get('id', None)
            if id is None:
                return Response({"result": False, "error": "Invalid product ID!"}, status=400)

            prd = products.objects.filter(id=id).first()
            if not prd:
                return Response({"result": False, "error": "Product not found!"}, status=404)

            if prd.image:
                prd.image.delete(save=False)

            prd.delete() 

            return Response({"result": True, "message": "Product deleted successfully."}, status=200)

        except Exception as e:
            logger.error(f"error in DelPrd: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)

class EditProductView(APIView):
    def post(self, request):
        try:
            form = edit_prd(request.POST, request.FILES)
            if form.is_valid():
                if not request.user.is_authenticated:
                    return Response({"result": False, "error": "Login required to edit a product!"}, status=401)

                user = request.user
                id = form.cleaned_data["id"]
                name = form.cleaned_data["name"]
                discription = form.cleaned_data["discription"]
                price = int(form.cleaned_data["price"])
                currency_type = form.cleaned_data["currency_type"]
                image = form.cleaned_data.get("image", None)
                condition = form.cleaned_data["condition"]

                prd = products.objects.filter(id=id, user=user).first()
                if not prd:
                    return Response({"result": False, "error": "Product not found or permission denied."}, status=404)

                prd.name = name
                prd.discription = discription
                prd.price = price
                prd.currency_type = currency_type
                prd.condition = condition

                # set new image if exist
                if image:
                    if prd.image:
                        prd.image.delete(save=False)
                    prd.image = image

                prd.save()
                return Response({"result": True, "message": "Product updated successfully."}, status=200)

            return Response({"result": False, "error": "Invalid Data!"}, status=400)

        except Exception as e:
            logger.error(f"error in EditProductView: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)

class GetPrdComment(APIView):
    def get(self, request):
        try:
            id = request.GET.get('id', None)
            page = request.GET.get('page', 0)

            if id == None:
                return Response({"result": False, "error": "Invalid product ID!"}, status=400)
            
            prd = products.objects.filter(id=id).first()
            if not prd:
                return Response({"result": False, "error": "Product not found!"}, status=404)
            
            comments = ProductComment.objects.filter(product=prd)[page*3:(page+1)*3]

            comments_data = [{"text":comment.text, "user":comment.user.username} for comment in comments]
            return Response({"result": True, "comments": comments_data}, status=200)
        
        except Exception as e:
            logger.error(f"error in GetPrdComment: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)
            
class AddProductComment(APIView):
    def post(self, request):
        try:
            text = request.data.get('text', None)
            id = request.data.get('id', None)
            if not text or not id:
                return Response({"result": False, "error": "Invalid data!"}, status=400)
            
            prd = products.objects.filter(id=id).first()
            if not prd:
                return Response({"result": False, "error": "Product not found!"}, status=404)
            
            comment = ProductComment.objects.get_or_create(user=request.user, product=prd)[0]
            comment.text = text
            comment.save()
            return Response({"result": True, "message": "Comment added successfully."}, status=200)
        
        except Exception as e:
            logger.error(f"error in AddProductComment: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)