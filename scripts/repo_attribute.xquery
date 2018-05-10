xquery version "3.0";

declare namespace acc = "https://aspectc.org/schemas/ac-model";
declare namespace aofitfct = "https://ulrichgabor.de/aofit";
declare namespace aofitconfig = "https://ulrichgabor.de/aofit/config";

(: Searchs declaration of attribute with the fully qualified attribute name. :)
declare function aofitfct:findAttribute(
	$acmodel as element(acc:ac-model),
	$attributeFullQualifier as xs:string
) as element(acc:Attribute)? {
	let $tokenizedAttributeQualifier := tokenize($attributeFullQualifier, "::")
	let $_ := if ($tokenizedAttributeQualifier[1] != "")
		then error(xs:QName("notFullQualified"), "Attribute name is not a full qualified one.")
		else true()

	(: Split off the attribute name off the sequence. :)
	let $attributeName := $tokenizedAttributeQualifier[last()]
	let $namespaces := reverse(remove(reverse($tokenizedAttributeQualifier), 1))

	(: While the first namespace is empty, it is named "::" in the ac-model, so rename it. :)
	let $modelNamespaces := ("::", remove($namespaces, 1))

	(: Descend to the attribute, following the namespaces. :)
	let $lastNamespace := fold-left(
		function ($result, $cur) {
			$result/acc:Namespace[@name=$cur]/acc:children
		}, $acmodel/acc:root, $modelNamespaces
		)
	let $attribute := $lastNamespace/acc:Attribute[@name=$attributeName]
	return $attribute
};

(: Returns all parameters of an attribute on a specific call join point. :)
declare function aofitfct:getParametersofJPIDForAttribute(
	$acmodel as element(acc:ac-model),
	$attributeid as xs:integer,
	$jpid as xs:integer
) as element(acc:Parameter)* {
	$acmodel//acc:Call[@jpid=$jpid]/ancestor::*/acc:annotations/acc:Annotation[@attribute=$attributeid]/acc:parameters/acc:Parameter
};

(: Extracts repository filename and attributeQualifier from config file. :)
declare function local:parseConfig(
	$config as document-node(element(aofitconfig:config))
) as node()+ {
	let $acmodelfilename := $config//aofitconfig:repofilename
	let $attributeQualifier := $config//aofitconfig:attributeQualifier
	let $jpid := $config//aofitconfig:jpid
	return if(count($acmodelfilename) = 0 or count($attributeQualifier) = 0 or count($jpid) = 0) then (
			error(xs:QName("brokenConfiguration"), "Missing repository filename or attributeQualifier or jpid.")
		) else (
			($acmodelfilename, $attributeQualifier, $jpid)
		)
};

(: Open a repository file, check if it contains an ac-model node and return that. :)
declare function local:loadACModelFromRepositoryFilename(
	$repositoryFilename as xs:string
) as element(acc:ac-model) {
	let $repositoryFile := if (doc-available($repositoryFilename))
		then doc($repositoryFilename)
		else error(xs:QName("missingRepositoryFile"), "Repository file not found.")
	let $acmodel := if (count($repositoryFile/acc:ac-model) = 0)
		then error(xs:QName("missingACModel"), "No ac-model node in repository file.")
		else $repositoryFile/acc:ac-model
	return $acmodel
};

declare function local:main(
	$context as node()
) {
	let $config := local:parseConfig($context)
	let $acmodel := local:loadACModelFromRepositoryFilename($config[1])
	let $attributeQualifier := $config[2] cast as xs:string
	let $jpid := $config[3] cast as xs:integer
	let $_ := if (string-length($attributeQualifier) = 0)
		then error(xs:QName("emptyAttributeQualifier"), "Empty attribute qualifier.")
		else true()
	let $attribute := aofitfct:findAttribute($acmodel, $attributeQualifier)
	let $_ := if (count($attribute) = 0)
		then error(xs:QName("attributeNotFound"), "Attribute node not found.")
		else true()
	let $attributeid := $attribute/@id
	let $parameters := aofitfct:getParametersofJPIDForAttribute($acmodel, $attributeid, $jpid)/@expression
	return string-join($parameters, ",")
};

local:main(.)
