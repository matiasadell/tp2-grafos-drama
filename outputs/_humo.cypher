// Prueba de humo del runner (no se entrega).

// @paso H.1_conteo
MATCH (n) RETURN count(n) AS nodos;

// @paso H.2_profile medir=2
PROFILE MATCH (m:Movie) WHERE m.title STARTS WITH 'Toy' RETURN m.title AS titulo ORDER BY titulo LIMIT 3;
