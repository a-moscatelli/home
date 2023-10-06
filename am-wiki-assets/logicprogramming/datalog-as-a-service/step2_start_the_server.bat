M:
cd M:\DEV\A-MOSCATELLI-WIKI\logicprog-mastermind\maven
rem java -jar .\ext-libs\winstone-0.9.10.jar --warfile .\webapp1\target\my-web-app-1.0.0.war
java -jar .\ext-libs\jetty-runner-9.4.0.M1.jar --port 8080 .\webapp1\target\my-web-app-1.0.0.war --jar .\ext-libs\AbcDatalog-0.6.0.jar
