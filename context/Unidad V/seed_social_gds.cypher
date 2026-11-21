// Unidad V — grafo social ampliado (Neo4j Desktop LOCAL, con GDS).
// 13 usuarios, 18 relaciones FOLLOWS. Dos comunidades + puente (Marcos) + par aislado.
MATCH (n) DETACH DELETE n;
CREATE CONSTRAINT user_name IF NOT EXISTS FOR (u:User) REQUIRE u.name IS UNIQUE;
CREATE
  (ana:User   {name:'Ana',    intereses:['ia','grafos','musica']}),
  (beto:User  {name:'Beto',   intereses:['ia','grafos']}),
  (carla:User {name:'Carla',  intereses:['grafos','viajes']}),
  (dario:User {name:'Dario',  intereses:['ia','musica']}),
  (elena:User {name:'Elena',  intereses:['grafos','musica']}),
  (fabio:User {name:'Fabio',  intereses:['deportes','viajes']}),
  (gina:User  {name:'Gina',   intereses:['deportes','cine']}),
  (hugo:User  {name:'Hugo',   intereses:['deportes','viajes']}),
  (ivan:User  {name:'Ivan',   intereses:['cine','viajes']}),
  (julia:User {name:'Julia',  intereses:['deportes','cine']}),
  (marcos:User{name:'Marcos', intereses:['grafos','deportes']}),
  (nora:User  {name:'Nora',   intereses:['cocina','cine']}),
  (omar:User  {name:'Omar',   intereses:['cocina','viajes']}),
  // Comunidad A
  (ana)-[:FOLLOWS]->(beto), (beto)-[:FOLLOWS]->(carla), (carla)-[:FOLLOWS]->(ana),
  (ana)-[:FOLLOWS]->(dario), (dario)-[:FOLLOWS]->(elena), (elena)-[:FOLLOWS]->(ana),
  (beto)-[:FOLLOWS]->(elena),
  // Comunidad B
  (fabio)-[:FOLLOWS]->(gina), (gina)-[:FOLLOWS]->(hugo), (hugo)-[:FOLLOWS]->(fabio),
  (fabio)-[:FOLLOWS]->(ivan), (ivan)-[:FOLLOWS]->(julia), (julia)-[:FOLLOWS]->(fabio),
  (gina)-[:FOLLOWS]->(julia),
  // Puente (una sola dirección) y par aislado
  (carla)-[:FOLLOWS]->(marcos), (marcos)-[:FOLLOWS]->(fabio),
  (nora)-[:FOLLOWS]->(omar), (omar)-[:FOLLOWS]->(nora);
