from django.http import HttpResponse
import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import DatasetA
from .serializers import DatasetASerializer
from .models import DatasetB,Ecart
from .serializers import EcartSerializer
from .models import Ecart
from .serializers import DatasetBSerializer
import time

from django.db.models import F
from itertools import chain
from collections import defaultdict
from django.db import connection
def index(request):
    return HttpResponse("Bienvenue dans l'app Spark !")

def reset_dataset_a_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE spark_dataseta_id_seq RESTART WITH 1;")  

def reset_Ecart_id_sequence() :
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE spark_Ecart_id_seq RESTART WITH 1;")  


def reset_dataset_b_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE spark_datasetb_id_seq RESTART WITH 1;")  
# ------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def dataset_a_view(request):
    if request.method == 'GET':
        queryset = DatasetA.objects.all()[:1000]  # Limite à 1000 lignes
        serializer = DatasetASerializer(queryset, many=True)
        return Response({
            "count": DatasetA.objects.count(),  
            "data": serializer.data
        })


    if request.method == 'POST':
        try:
            n = int(request.data.get("nombre", 10))
            if n <= 0:
                return Response({"error": "Le nombre doit être supérieur à 0"}, status=400)

            DatasetA.objects.all().delete()
            reset_dataset_a_id_sequence()

            batch_size = 50000
            created_count = 0
            total_batches = (n // batch_size) + (1 if n % batch_size else 0)

            for batch_index, start in enumerate(range(1, n + 1, batch_size), 1):
                end = min(start + batch_size, n + 1)
                batch = [
                    DatasetA(nom=f"Item_A_{i}", valeur=random.randint(1, 1000))
                    for i in range(start, end)
                ]
                DatasetA.objects.bulk_create(batch)
                created_count += len(batch)

                # Message de suivi
                print(f"[Batch {batch_index}/{total_batches}] Insertion de {len(batch)} lignes...")

            return Response({
                "message": f"{created_count} lignes insérées avec succès dans DatasetA"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    elif request.method == 'DELETE':
        deleted_count, _ = DatasetA.objects.all().delete()
        return Response({"message": f"{deleted_count} lignes supprimées de DatasetA."})


@api_view(['GET', 'POST', 'DELETE'])
def dataset_b_view(request):
    if request.method == 'GET':
        queryset = DatasetB.objects.all()[:1000]  # Limite à 1000 lignes
        serializer = DatasetBSerializer(queryset, many=True)
        return Response({
            "count": DatasetB.objects.count(),  
            "data": serializer.data
        })

    elif request.method == 'POST':
        try:
            n = int(request.data.get("nombre", 10))
            if n <= 0:
                return Response({"error": "Le nombre doit être supérieur à 0"}, status=400)

            DatasetB.objects.all().delete()
            reset_dataset_b_id_sequence()

            batch_size = 50000
            created_count = 0
            total_batches = (n // batch_size) + (1 if n % batch_size else 0)

            for batch_index, start in enumerate(range(1, n + 1, batch_size), 1):
                end = min(start + batch_size, n + 1)
                batch = [
                    DatasetB(nom=f"Item_B_{i}", valeur=random.randint(1, 1000))
                    for i in range(start, end)
                ]
                DatasetB.objects.bulk_create(batch)
                created_count += len(batch)

                # Message de suivi
                print(f"[Batch {batch_index}/{total_batches}] Insertion de {len(batch)} lignes...")

            return Response({
                "message": f"{created_count} lignes insérées avec succès dans DatasetB"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


    elif request.method == 'DELETE':
        count = DatasetB.objects.count()
        DatasetB.objects.all().delete()
        return Response(
            {"message": f"{count} lignes supprimées de DatasetB"},
            status=status.HTTP_200_OK
        )









@api_view(['POST', 'DELETE'])
def comparer_datasets(request):
    if request.method == 'DELETE':
        # Nettoyage de la table Ecart
        Ecart.objects.all().delete()
        reset_Ecart_id_sequence()
        return Response({"message": "Table Ecart vidée et ID réinitialisé."}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        methode = request.data.get("methode", "Django")

        # Nettoyage de la table Ecart
        Ecart.objects.all().delete()
        reset_Ecart_id_sequence()

        start_time = time.time()

        try:
            # Appel à la bonne méthode
            if methode == "Spark":
                comparer_avec_spark(limit=None)   
            else:
                comparer_avec_django()

            execution_time = round(time.time() - start_time, 3)
            print("le temps : " + str(execution_time))

            # Statistiques
            count_ecart = Ecart.objects.count()
            count_identique = Ecart.objects.filter(status="Identique").count()
            count_different = Ecart.objects.filter(status="Différent").count()
            count_nouveau = Ecart.objects.filter(status="Nouveau").count()

            # Résultats limités à 1000
            serialized_data = EcartSerializer(Ecart.objects.all().order_by('id')[:1000], many=True)
            # ✅ Affichage console
            print("=== Résultat de la comparaison ===")
            print(f"Temps d'exécution : {execution_time} secondes")
            print(f"Nombre total d'écarts : {count_ecart}")
            print(f"  → Identiques : {count_identique}")
            print(f"  → Différents : {count_different}")
            print(f"  → Nouveaux : {count_nouveau}")
            print("=== Fin du résumé ===")
            return Response({
                "execution_time_seconds": execution_time,
                "total_ecarts": count_ecart,
                "count_identique": count_identique,
                "count_different": count_different,
                "count_nouveau": count_nouveau,
                "data": serialized_data.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# -----------------------------------------


# Méthode Django
def comparer_avec_django():
    import gc

    chunk_size = 100000
    last_id = 0
    total_inserted = 0

    print("[INFO] Démarrage de la comparaison en chunks...")

    while True:
        # Charger un chunk de A
        chunk_a = dict(DatasetA.objects.filter(id__gt=last_id).order_by("id").values_list("id", "valeur")[:chunk_size])
        # Charger le chunk correspondant de B
        chunk_b = dict(DatasetB.objects.filter(id__gt=last_id).order_by("id").values_list("id", "valeur")[:chunk_size])

        # Si les deux sont vides, on a fini
        if not chunk_a and not chunk_b:
            break

        # Fusion des IDs dans ce chunk
        all_ids = sorted(set(chunk_a.keys()).union(chunk_b.keys()))
        if not all_ids:
            break

        batch = []
        for id_ in all_ids:
            val_a = chunk_a.get(id_)
            val_b = chunk_b.get(id_)

            if val_a is not None and val_b is not None:
                if val_a == val_b:
                    status = "Identique"
                    ecart_valeur = "0"
                else:
                    status = "Différent"
                    ecart_valeur = str(abs(val_a - val_b))
            else:
                status = "Nouveau"
                ecart_valeur = str(val_a if val_a is not None else val_b)

            batch.append(Ecart(
                nom=f"ItemAB_{id_}",
                ecart_valeur=ecart_valeur,
                status=status,
                methode="Django"
            ))

        # Insertion du batch
        Ecart.objects.bulk_create(batch)
        total_inserted += len(batch)
        print(f"[Chunk] ID max traité = {max(all_ids)} → {len(batch)} écarts insérés (total = {total_inserted})")

        last_id = max(all_ids)
        gc.collect()

    print(f"[INFO] Comparaison terminée. Total écarts insérés : {total_inserted}")

# Méthode Django




def comparer_avec_spark(limit: int | None = None) :


    # ── Imports internes ───────────────────────────────────────────────────────
    import os, math, psutil, time
    from django.conf import settings
    from django.db import connection
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, when, lit, concat, coalesce, abs as spark_abs
    from pyspark.sql.types import StringType
    # ───────────────────────────────────────────────────────────────────────────



    # Helper pour récupérer (min_id, max_id)
    def _id_bounds(table: str) -> tuple[int, int]:
        with connection.cursor() as cur:
            cur.execute(f"SELECT MIN(id), MAX(id) FROM {table};")
            lo, hi = cur.fetchone()
        return (lo or 1, hi or 1)

    # 1) Configuration JDBC
    db = settings.DATABASES["default"]
    jdbc_url = (
        f"jdbc:postgresql://{db['HOST']}:{db['PORT']}/{db['NAME']}"
        "?reWriteBatchedInserts=true"
    )
    jdbc_props = {
        "user": db["USER"],
        "password": db["PASSWORD"],
        "driver": "org.postgresql.Driver",
    }

    # 2) Volume de données → partitions
    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM spark_dataseta")
        rows_a = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM spark_datasetb")
        rows_b = cur.fetchone()[0]
    total_rows = max(rows_a, rows_b) if limit is None else limit
    num_parts = max(4, min(64, math.ceil(total_rows / 250_000)))  # ~250 k lignes/part

    # 3) RAM dispo → mémoire driver
    avail_gb = psutil.virtual_memory().available // (1024**3)
    driver_gb = max(1, min(16, int(avail_gb * 0.60)))
    driver_mem = f"{driver_gb}g"

    # 4) Session Spark
    spark = (
        SparkSession.builder.appName("Compare_AB_Auto")
        .master("local[*]")
        .config("spark.driver.memory", driver_mem)
        .config("spark.sql.shuffle.partitions", str(num_parts * 4))
        .config("spark.sql.adaptive.enabled", "true")        # AQE
        .config(
            "spark.driver.extraClassPath",
            os.path.join(settings.BASE_DIR, "jdbc", "postgresql-42.7.3.jar"),
        )
        .getOrCreate()
    )

    # 5) Bornes id globales
    lo_a, hi_a = _id_bounds("spark_dataseta")
    lo_b, hi_b = _id_bounds("spark_datasetb")
    lo, hi = min(lo_a, lo_b), max(hi_a, hi_b)

    # Sous-requête si limit
    def _dbtable(tbl: str) -> str:
        return tbl if limit is None else f"(SELECT * FROM {tbl} LIMIT {limit}) AS sub"

    # 6) Lecture partitionnée
    def _read(tbl: str):
        return (
            spark.read.format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", _dbtable(tbl))
            .option("user", jdbc_props["user"])
            .option("password", jdbc_props["password"])
            .option("driver", jdbc_props["driver"])
            .option("partitionColumn", "id")
            .option("lowerBound", str(lo))
            .option("upperBound", str(hi))
            .option("numPartitions", str(num_parts))
            .option("fetchsize", "10000")
            .load()
            .select("id", "valeur")
        )

    df_a, df_b = _read("spark_dataseta"), _read("spark_datasetb")

    # 7) Jointure + calcul des écarts
    res_df = (
        df_a.alias("a")
        .join(df_b.alias("b"), "id", "full")
        .select(
            coalesce(col("a.id"), col("b.id")).alias("id"),
            col("a.valeur").alias("val_a"),
            col("b.valeur").alias("val_b"),
        )
        .withColumn(
            "status",
            when(col("val_a").isNull() | col("val_b").isNull(), "Nouveau")
            .when(col("val_a") == col("val_b"), "Identique")
            .otherwise("Différent"),
        )
        .withColumn(
            "ecart_valeur",
            when(col("status") == "Identique", lit("0")).otherwise(
                spark_abs(
                    coalesce(col("val_a"), lit(0)) - coalesce(col("val_b"), lit(0))
                ).cast(StringType())
            ),
        )
        .withColumn("nom", concat(lit("ItemAB_"), col("id")))
        .withColumn("methode", lit("Spark"))
        .select("nom", "ecart_valeur", "status", "methode")
    )

    # 8) Écriture parallèle dans spark_ecart
    (
        res_df.write.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "spark_ecart")
        .option("user", jdbc_props["user"])
        .option("password", jdbc_props["password"])
        .option("driver", jdbc_props["driver"])
        .option("batchsize", "10000")
        .mode("append")
        .save()
    )

    spark.stop()
    




# ---------------------------------



