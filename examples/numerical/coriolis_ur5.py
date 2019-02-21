import casadi as cs
from urdf_parser_py.urdf import URDF, Pose
import os # For current directory
import urdf2casadi.urdf2casadi.urdfparser
import urdf2casadi.urdf2casadi.geometry.plucker as plucker
import numpy as np
import PyKDL as kdl
import kdl_parser.kdl_parser_py.kdl_parser_py.urdf as kdlurdf

ok, ur_tree = kdlurdf.treeFromFile('./urdf2casadi/examples/urdf/ur5.urdf')
asd = urdf2casadi.urdf2casadi.urdfparser.URDFparser()
robot_desc = asd.from_file("./urdf2casadi/examples/urdf/ur5.urdf")
root = 'base_link'
tip = 'wrist_3_link'
ur_chain = ur_tree.getChain(root,tip)

jointlist, names, q_max, q_min = asd.get_joint_info(root, tip)
n_joints = len(jointlist)
q = kdl.JntArray(n_joints)
grav = kdl.Vector()
qdot = kdl.JntArray(n_joints)
res_kdl = kdl.JntArray(n_joints)
C = asd.get_jointspace_bias_matrix(root, tip)
error = np.zeros(n_joints)

def u2c2np(asd):
    return cs.Function("temp",[],[asd])()["o0"].toarray()

def kdl2np(asd):
    x = (asd[0], asd[1], asd[2], asd[3], asd[4], asd[5])
    return np.asarray(x)

n_itr = 1000
for i in range(n_itr):
    for j in range(n_joints):
        q[j] = (q_max[j] - q_min[j])*np.random.rand()-(q_max[j] - q_min[j])/2
        qdot[j] = (q_max[j] - q_min[j])*np.random.rand()-(q_max[j] - q_min[j])/2

    kdl.ChainDynParam(ur_chain, grav).JntToCoriolis(q, qdot, res_kdl)
    res_u2c = C(q,qdot)

    for tau_idx in range(n_joints):
        error[tau_idx] += np.absolute((kdl2np(res_kdl)[tau_idx] - u2c2np(res_u2c)[tau_idx]))

print "Errors in coriolis forces with",n_itr, "iterations and comparing against KDL:\n", error

sum_error = 0
for err in range(n_joints):
    sum_error += error[err]
print "Sum of errors:\n", sum_error
