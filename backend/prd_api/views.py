from logger import logger
from .models import Product, ProductStars, ProductInCart, ProductComment
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .forms import add_prd, edit_prd
from .Choise_Data import *
from django.contrib.auth.models import User
import math

class get_products(APIView):
    def get(self, request):
        try:
            page = request.query_params.get('page', None)
            product_id = request.query_params.get("id", None)
            by_user = request.query_params.get("by_user", None)
            category = request.query_params.get("category", None)

            if page != None :
                page = int(page)
                search_sts = request.query_params.get('search', "0")

                if search_sts == "0" or search_sts == None:
                    product_qs = Product.objects.all()[page*6:(page+1)*6] 
                else:
                    search_sts = str(search_sts)
                    if search_sts != "1":
                        return Response({"products": False, "error": "search parameter is invalid"}, status=400)
                    search_text = request.query_params.get('search_text', None)
                    if search_text == None:
                        return Response({"products": False, "error": "search_text parameter is required to search"}, status=400)
                    search_text = str(search_text)
                    product_qs = Product.objects.filter(Q(name__icontains=search_text) | Q(discription__icontains=search_text))[page*6:(page+1)*6]
            
            elif category != None :
                category = str(category)
                product_qs = Product.objects.filter(category=category)

            elif product_id != None :
                product_id = int(product_id)
                product_qs = Product.objects.filter(id=product_id)
            
            elif by_user != None :
                product_qs = Product.objects.filter(user=request.user)

            else :
                product_qs = Product.objects.all()

            # get number of registered users
            try:
                users_count = User.objects.count()
                if users_count == 0:
                    return Response({"products": False, "error": "Couldn't find nothing in site"}, status=500)
            except:
                return Response({"products": False, "error": "Couldn't find nothing in site"}, status=500)

            data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.discription,
                    "price": p.price,
                    "currency_type": p.currency_type,
                    "image": p.image.url if p.image else None,
                    "stars": p.stars // users_count if p.stars else 0,
                    "condition": p.condition,
                    "category": p.category,
                }
                for p in product_qs
            ]

            return Response({"products": data})
        
        except Exception as e:
            logger.error(f"error in get_products: {e}")
            return Response({"products": False}, status=500)

class search_products(APIView):
    def get(self, request):
        try:
            category = request.query_params.get("category", None)
            search_text = request.query_params.get("search_text", None)
            page = request.query_params.get("page", None)

            if page == None:
                return Response({"products": False, "error": "page parameter is required"}, status=400)

            # validate page value
            try:
                page = int(page)
            except:
                return Response({"products": False, "error": "page parameter is invalid"}, status=400)

            if category == None and search_text == None:
                return Response({"products": False, "error": "category and search_text parameters are required"}, status=400)

            # search in a category
            if category != None and search_text == None:
                try:
                    category = str(category)
                except:
                    return Response({"products": False, "error": "category parameter is invalid"}, status=400)
                
                if category not in [c[0] for c in CATEGORIES_CHOICES]:
                    return Response({"products": False, "error": "category parameter is invalid"}, status=400)

                product_qs = Product.objects.filter(category=category)
            
            # search in a product name or discription
            elif search_text != None and category == None:
                try:
                    search_text = str(search_text)
                except:
                    return Response({"products": False, "error": "search_text parameter is invalid"}, status=400)
                
                product_qs = Product.objects.filter(Q(name__icontains=search_text) | Q(description__icontains=search_text))
            
            
            # search with both of category and search_text
            else:
                try:
                    category = str(category)
                    search_text = str(search_text)
                except:
                    return Response({"products": False, "error": "category or search_text parameters are invalid"}, status=400)

                if category not in [c[0] for c in CATEGORIES_CHOICES]:
                    return Response({"products": False, "error": "category parameter is invalid"}, status=400)

                product_qs = Product.objects.filter(Q(name__icontains=search_text) | Q(description__icontains=search_text), category=category)
            
            # get number of registered users
            try:
                users_count = User.objects.count()
                if users_count == 0:
                    return Response({"products": False, "error": "Couldn't find nothing in site"}, status=500)
            except:
                return Response({"products": False, "error": "Couldn't find nothing in site"}, status=500)
            
            # get number of pages
            try:
                products_count = product_qs.count()
                totalPages = math.ceil(products_count / 6)
            except:
                totalPages = 0

            # slice products
            product_qs = product_qs[page*6:(page+1)*6]

            # prepare data
            data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "currency_type": p.currency_type,
                    "image": p.image.url if p.image else None,
                    "stars": p.stars // users_count if p.stars else 0,
                    "category": p.category,
                }
                for p in product_qs
            ]

            return Response({"products": data, "totalPages":totalPages}, status=200)

        except Exception as e:
            logger.error(f"error in search_products: {e}")
            return Response({"products": False, "error":"error in searching"}, status=500)

class getPrdByID(APIView):
    def get(self, request):
        try:
            prd_id = request.query_params.get('id')
            if not prd_id:
                return Response({"product": False, "error": "prd_ID parameter is required"}, status=400)

            try:
                prd_id = int(prd_id)
            except:
                return Response({"product": False, "error": "Invalid product ID !"}, status=400)
            product = Product.objects.filter(id=prd_id).first()
            if not product:
                return Response({"product": False, "error": "Product not found"}, status=404)
            data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "currency_type": product.currency_type,
                "image": product.image.url if product.image else None,
                "stars": product.stars // User.objects.count() if product.stars else 0,
                "category": product.category,
            }
            return Response({"product": data}, status=200)
        except Exception as e:
            logger.error(f"error in getPrdByID: {e}")
            return Response({"product": False, "error":"error in getting product"}, status=500)
        
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

                if not Product.objects.filter(id=prd_id).exists():
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
                    product = Product.objects.get(id=prd_id)
                except Product.DoesNotExist:
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

                if not Product.objects.filter(id=prd_id).exists():
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
                    product = Product.objects.get(id=prd_id)
                except Product.DoesNotExist:
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
                    category = form.cleaned_data["category"]

                    prd = Product.objects.create(user=user, name=name, discription=discription, price=price, currency_type=currency_type, image=image, condition=condition, category=category)
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

            prd = Product.objects.filter(id=id).first()
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
                category = form.cleaned_data["category"]

                prd = Product.objects.filter(id=id, user=user).first()
                if not prd:
                    return Response({"result": False, "error": "Product not found or permission denied."}, status=404)

                prd.name = name
                prd.discription = discription
                prd.price = price
                prd.currency_type = currency_type
                prd.condition = condition
                prd.category = category

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
            
            prd = Product.objects.filter(id=id).first()
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

            if not request.user.is_authenticated:
                return Response({"result": False, "error": "Login required to add a comment!"}, status=401)

            if not text or not id:
                return Response({"result": False, "error": "Invalid data!"}, status=400)
            
            prd = Product.objects.filter(id=id).first()
            if not prd:
                return Response({"result": False, "error": "Product not found!"}, status=404)
            
            comment = ProductComment.objects.get_or_create(user=request.user, product=prd)[0]
            comment.text = text
            comment.save()
            return Response({"result": True, "message": "Comment added successfully."}, status=200)
        
        except Exception as e:
            logger.error(f"error in AddProductComment: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)
        
class getChoiseData(APIView):
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({"result": False, "error": "Login required!"}, status=401)

            data = {
                "currency_type": CURRENCY_CHOICES,
                "categories": CATEGORIES_CHOICES
            }
            return Response({"result": True, "data": data}, status=200)

        except Exception as e:
            logger.error(f"error in getChoiseData: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)
        
class getCategories(APIView):
    def get(self, request):
        try:
            #if not request.user.is_authenticated:
             #   return Response({"result": False, "error": "Login required!"}, status=401)

            data = {
                "categories": CATEGORIES_CHOICES
            }
            return Response({"result": True, "data": data}, status=200)

        except Exception as e:
            logger.error(f"error in getCategories: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)

class AllProductIDs(APIView):
    def get(self, request):
        product_qs = Product.objects.all()
        data = [
            {
                "id": p.id,
            }
            for p in product_qs]

        return Response({"products": data})

class GetTopPrds(APIView):
    def get(self, request):
        try:
            top_prds = Product.objects.all().order_by('-stars')[:10]
            data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "image": p.image.url if p.image else None,
                }
                for p in top_prds]
            return Response({"result": data, "products": data}, status=200)
        except Exception as e:
            logger.error(f"error in GetTopPrds: {e}")
            return Response({"result": False, "error": "Server error."}, status=500)


